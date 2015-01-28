# Copyright 2014 - Rackspace Hosting
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

"""Solum Deployer Heat handler."""

import socket
import time

from heatclient import exc
import httplib2
from oslo.config import cfg
from sqlalchemy import exc as sqla_exc
import yaml

from solum.common import catalog
from solum.common import clients
from solum.common import exception
from solum.common import heat_utils
from solum.common import repo_utils
from solum.conductor import api as conductor_api
from solum import objects
from solum.objects import assembly
from solum.openstack.common import log as logging


LOG = logging.getLogger(__name__)

STATES = assembly.States

OPT_GROUP = cfg.OptGroup(name='deployer',
                         title='Options for the solum-deployer service')
SERVICE_OPTS = [
    cfg.IntOpt('max_attempts',
               default=600,
               help=('Number of attempts to query the Heat stack for '
                     'finding out the status of the created stack and '
                     'getting url of the DU created in the stack')),
    cfg.IntOpt('du_attempts',
               default=240,
               help=('Number of attempts to query the Docker DU for '
                     'finding out the status of the created app and '
                     'getting url of the DU created in the stack')),
    cfg.IntOpt('wait_interval',
               default=1,
               help=('Sleep time interval between two attempts of querying '
                     'the Heat stack. This interval is in seconds.')),
    cfg.FloatOpt('growth_factor',
                 default=1.1,
                 help=('Factor by which sleep time interval increases. '
                       'This value should be >= 1.0')),
    cfg.StrOpt('flavor',
               default="m1.tiny",
               help='VM Flavor'),
]

cfg.CONF.register_group(OPT_GROUP)
cfg.CONF.register_opts(SERVICE_OPTS, OPT_GROUP)
cfg.CONF.import_opt('image_format', 'solum.api.handlers.assembly_handler',
                    group='api')
cfg.CONF.import_group('worker', 'solum.worker.handlers.shell')


def update_assembly(ctxt, assembly_id, data):
    conductor_api.API(context=ctxt).update_assembly(assembly_id, data)


class Handler(object):
    def __init__(self):
        super(Handler, self).__init__()
        objects.load()

    def echo(self, ctxt, message):
        LOG.debug("%s" % message)

    def _get_stack_name(self, assembly, prefix_len=100):
        assem_name = assembly.name
        # heat stack name has a max allowable length of 255
        return ''.join([assem_name[:min(len(assem_name), prefix_len)], '-',
                        assembly.uuid])

    def destroy(self, ctxt, assem_id):
        assem = objects.registry.Assembly.get_by_id(ctxt, assem_id)
        stack_id = self._find_id_if_stack_exists(assem)

        if stack_id is not None:
            osc = clients.OpenStackClients(ctxt)
            osc.heat().stacks.delete(stack_id)

            wait_interval = cfg.CONF.deployer.wait_interval
            growth_factor = cfg.CONF.deployer.growth_factor
            stack_name = self._get_stack_name(assem)
            for count in range(cfg.CONF.deployer.max_attempts):
                stack_id = self._get_stack_id_from_heat(osc, stack_name)
                if stack_id is None:
                    break
                time.sleep(wait_interval)
                wait_interval *= growth_factor

        if stack_id is None:
            assem.destroy(ctxt)
            return

        if stack_id is not None:
            update_assembly(ctxt, assem_id,
                            {'status': STATES.ERROR_STACK_DELETE_FAILED})

    def deploy(self, ctxt, assembly_id, image_id):
        osc = clients.OpenStackClients(ctxt)

        assem = objects.registry.Assembly.get_by_id(ctxt,
                                                    assembly_id)

        if cfg.CONF.api.image_format == 'docker':
            parameters = {'app_name': assem.name,
                          'image': image_id}
            parameters.update(heat_utils.get_network_parameters(osc))

            # TODO(asalkeld) support template flavors
            # (maybe an autoscaling one)
            # this could also be stored in glance.
            template_flavor = 'basic'
        elif cfg.CONF.api.image_format == 'vm':
            # use coreos
            parameters = {}
            parameters['name'] = str(assem.uuid)

            # TODO(devkulkarni): optimized for devstack
            # We would read these from config files
            parameters['count'] = 1
            parameters['flavor'] = cfg.CONF.deployer.flavor
            template_flavor = 'coreos'
        else:
            image_fmt = cfg.CONF.api.image_format
            LOG.debug("Image format is %s not supported." % image_fmt)
            update_assembly(ctxt, assembly_id, {'status': STATES.ERROR})
            return

        try:
            template = catalog.get('templates', template_flavor)
        except exception.ObjectNotFound as onf_ex:
            LOG.excepion(onf_ex)
            update_assembly(ctxt, assembly_id, {'status': STATES.ERROR})
            return

        if cfg.CONF.api.image_format == 'vm':
            if cfg.CONF.worker.image_storage == 'docker_registry':
                template = self._get_template_for_docker_reg(assem, template)
                LOG.debug(template)
            elif cfg.CONF.worker.image_storage == 'swift':
                template = self._get_template_for_swift(assem,
                                                        template,
                                                        image_id)
            else:
                LOG.debug("DU storage option not recognized. Exiting..")
                update_assembly(ctxt, assembly_id, {'status': STATES.ERROR})
                return

        stack_name = self._get_stack_name(assem)
        stack_id = self._find_id_if_stack_exists(assem)

        if assem.status == STATES.DELETING:
            return

        if stack_id is not None:
            osc.heat().stacks.update(stack_id,
                                     stack_name=stack_name,
                                     template=template,
                                     parameters=parameters)
        else:
            try:
                created_stack = osc.heat().stacks.create(stack_name=stack_name,
                                                         template=template,
                                                         parameters=parameters)
            except Exception as exp:
                LOG.error("Error creating Heat Stack for,"
                          " assembly %s" % assembly_id)
                LOG.exception(exp)
                update_assembly(ctxt, assembly_id, {'status': STATES.ERROR})
                return
            stack_id = created_stack['stack']['id']

            LOG.debug("Stack id: %s" % stack_id)

            comp_name = 'Heat_Stack_for_%s' % assem.name
            comp_description = 'Heat Stack %s' % (
                yaml.load(template).get('description'))
            try:
                objects.registry.Component.assign_and_create(
                    ctxt, assem, comp_name, 'heat_stack', comp_description,
                    created_stack['stack']['links'][0]['href'], stack_id)
            except sqla_exc.IntegrityError:
                LOG.error("IntegrityError in creating Heat Stack component,"
                          " assembly %s may be deleted" % assembly_id)
                update_assembly(ctxt, assembly_id, {'status': STATES.ERROR})
                return
        update_assembly(ctxt, assembly_id, {'status': STATES.DEPLOYING})

        self._check_stack_status(ctxt, assembly_id, osc, stack_id)

    def _check_stack_status(self, ctxt, assembly_id, osc, stack_id):

        wait_interval = cfg.CONF.deployer.wait_interval
        growth_factor = cfg.CONF.deployer.growth_factor

        for count in range(cfg.CONF.deployer.max_attempts):
            stack = osc.heat().stacks.get(stack_id)
            if stack.status == 'COMPLETE':
                break
            elif stack.status == 'FAILED':
                update_assembly(ctxt, assembly_id,
                                {'status': STATES.ERROR_STACK_CREATE_FAILED})
                return
            time.sleep(wait_interval)
            wait_interval *= growth_factor

        if stack.status == "":
            update_assembly(ctxt, assembly_id,
                            {'status': STATES.ERROR_STACK_CREATE_FAILED})
            return

        host_url = self._parse_server_url(stack)
        if host_url is not None:
            du_is_up = False
            to_upd = {'status': STATES.WAITING_FOR_DOCKER_DU,
                      'application_uri': host_url}
            update_assembly(ctxt, assembly_id, to_upd)
            du_url = "http://" + host_url
            LOG.debug("DU URL:%s" % du_url)
            for count1 in range(cfg.CONF.deployer.du_attempts):
                time.sleep(1)
                try:
                    conn = repo_utils.get_http_connection()
                    resp, _ = conn.request(du_url, 'GET')
                    if resp is not None:
                        if resp['status'] == '200':
                            du_is_up = True
                            break
                except socket.timeout:
                    pass
                except (httplib2.HttpLib2Error, socket.error) as serr:
                    LOG.exception(serr)
                except Exception as exp:
                    LOG.exception(exp)
                    update_assembly(ctxt, assembly_id,
                                    {'status': STATES.ERROR})
                    return
            if du_is_up:
                to_update = {'status': STATES.READY,
                             'application_uri': host_url}
                update_assembly(ctxt, assembly_id, to_update)
            else:
                to_upd = {'status': STATES.ERROR_DU_CREATION}
                update_assembly(ctxt, assembly_id, to_upd)
        else:
            LOG.exception("Could not parse url from heat stack.")
            update_assembly(ctxt, assembly_id,
                            {'status': STATES.ERROR})

    def _parse_server_url(self, heat_output):
        """Parse server url from heat-stack-show output."""
        if 'outputs' in heat_output._info:
            return heat_output._info['outputs'][1]['output_value']
        return None

    def _find_id_if_stack_exists(self, assem):
        if assem.heat_stack_component is not None:
            return assem.heat_stack_component.heat_stack_id
        return None

    def _get_stack_id_from_heat(self, osc, stack_name):
        try:
            stack = osc.heat().stacks.get(stack_name)
            if stack is not None:
                return stack.identifier.split('/')[-1]
        except exc.HTTPNotFound:
            return None

    def _get_template_for_docker_reg(self, assem, template):
        template_bdy = yaml.safe_load(template)
        run_docker = "#!/bin/bash -x\n #Invoke the container\n"
        docker_endpt = cfg.CONF.worker.docker_reg_endpoint
        run_docker += "docker run -p 80:5000 -d "
        run_docker += docker_endpt + ":5042/"
        run_docker += str(assem.uuid)
        LOG.debug("run_docker:%s" % run_docker)
        comp_instance = template_bdy['resources']['compute_instance']
        user_data = comp_instance['properties']['user_data']
        user_data['str_replace']['template'] = run_docker
        comp_instance['properties']['user_data'] = user_data
        template_bdy['resources']['compute_instance'] = comp_instance
        template = yaml.dump(template_bdy)
        return template

    def _get_template_for_swift(self, assem, template, image_tar_location):
        template_bdy = yaml.safe_load(template)
        # TODO(devkulkarni): extract below DU values from assembly
        du_tar_file_name = "du_tar_file_name"
        du_name = "du_name"

        run_docker = "#!/bin/bash -x\n #Invoke the container\n"
        run_docker += "wget -q --tries=3 " + image_tar_location
        run_docker += "docker load < " + du_tar_file_name
        run_docker += "docker run -p 8080:5000 -d " + du_name
        run_docker += str(assem.uuid)
        comp_instance = template_bdy['resources']['compute_instance']
        user_data = comp_instance['properties']['user_data']
        user_data['str_replace']['template'] = run_docker
        comp_instance['properties']['user_data'] = user_data
        template_bdy['resources']['compute_instance'] = comp_instance
        template = yaml.dump(template_bdy)
        return template
