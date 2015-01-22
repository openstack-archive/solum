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

import time

from heatclient import exc
from oslo.config import cfg
from sqlalchemy import exc as sqla_exc
import yaml

from solum.common import catalog
from solum.common import clients
from solum.common import exception
from solum.common import heat_utils
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
               default=2000,
               help=('Number of attempts to query the Heat stack for '
                     'finding out the status of the created stack and '
                     'getting url of the DU created in the stack')),
    cfg.IntOpt('wait_interval',
               default=1,
               help=('Sleep time interval between two attempts of querying '
                     'the Heat stack. This interval is in seconds.')),
    cfg.FloatOpt('growth_factor',
                 default=1.1,
                 help=('Factor by which sleep time interval increases. '
                       'This value should be >= 1.0')),
]

cfg.CONF.register_group(OPT_GROUP)
cfg.CONF.register_opts(SERVICE_OPTS, OPT_GROUP)
cfg.CONF.import_opt('image_format', 'solum.api.handlers.assembly_handler',
                    group='api')


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
        parameters = {'app_name': assem.name,
                      'image': image_id}

        parameters.update(heat_utils.get_network_parameters(osc))

        # TODO(asalkeld) support template flavors (maybe an autoscaling one)
        #                this could also be stored in glance.
        template_flavor = 'basic'
        try:
            template = catalog.get('templates', template_flavor)
        except exception.ObjectNotFound as onf_ex:
            LOG.excepion(onf_ex)
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
            created_stack = osc.heat().stacks.create(stack_name=stack_name,
                                                     template=template,
                                                     parameters=parameters)
            stack_id = created_stack['stack']['id']

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
        got_stack_status = False

        for count in range(cfg.CONF.deployer.max_attempts):
            stack = osc.heat().stacks.get(stack_id)
            if stack.status == 'COMPLETE':
                host_url = self._parse_server_url(stack)
                if host_url is not None:
                    to_update = {'status': STATES.READY,
                                 'application_uri': host_url}
                    update_assembly(ctxt, assembly_id, to_update)
                    got_stack_status = True
                    break
            elif stack.status == 'FAILED':
                update_assembly(ctxt, assembly_id, {'status': STATES.ERROR})
                got_stack_status = True
                break

            time.sleep(wait_interval)
            wait_interval *= growth_factor

        if not got_stack_status:
            update_assembly(ctxt, assembly_id,
                            {'status': STATES.ERROR_STACK_CREATE_FAILED})

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
