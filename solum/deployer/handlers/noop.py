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

"""Solum Deployer noop handler."""

from oslo_log import log as logging

from solum import objects

LOG = logging.getLogger(__name__)


class Handler(object):
    def echo(self, ctxt, message):
        LOG.debug("%s" % message)

    def deploy(self, ctxt, assembly_id, image_id, ports):
        message = ("Deploy %s %s %s" % (assembly_id, image_id, ports))
        LOG.debug("%s" % message)

    def destroy_assembly(self, ctxt, assem_id):
        assem = objects.registry.Assembly.get_by_id(ctxt, assem_id)
        assem.destroy(ctxt)
        message = ("Destroy %s" % (assem_id))
        LOG.debug("%s" % message)

    def destroy_app(self, ctxt, app_id):
        message = ("Destroy App %s" % (app_id))
        LOG.debug("%s" % message)
