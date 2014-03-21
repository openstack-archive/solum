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

"""Solum Deployer default handler."""

import os
import yaml

from solum.common import clients
from solum import objects
from solum.openstack.common.gettextutils import _
from solum.openstack.common import log as logging


LOG = logging.getLogger(__name__)


class Handler(object):
    def echo(self, ctxt, message):
        LOG.debug(_("%s") % message)

    def deploy(self, ctxt, assembly_id, image_id):
        # TODO(asalkeld) support template flavors (maybe an autoscaling one)
        #                this could also be stored in glance.
        template_flavor = 'basic'

        proj_dir = os.path.join(os.path.dirname(__file__), '..', '..', '..')
        templ = os.path.join(proj_dir, 'etc', 'solum', 'templates',
                             '%s.yaml' % template_flavor)
        with open(templ) as templ_file:
            template = yaml.load(templ_file)

        osc = clients.OpenStackClients(ctxt)

        assem = objects.registry.Assembly.get_by_id(ctxt,
                                                    assembly_id)

        parameters = {'app_name': assem.name,
                      'image': image_id}
        stack_id = osc.heat().stacks.create(stack_name=assem.name,
                                            template=template,
                                            parameters=parameters)

        stack = osc.heat().stacks.get(**stack_id)
        comp_description = 'Heat Stack %s' % template.get('description')
        objects.registry.Component.assign_and_create(ctxt, assem,
                                                     'Heat Stack',
                                                     comp_description,
                                                     stack.identifier())
