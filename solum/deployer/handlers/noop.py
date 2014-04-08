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

from solum.openstack.common.gettextutils import _
from solum.openstack.common import log as logging

LOG = logging.getLogger(__name__)


class Handler(object):
    def echo(self, ctxt, message):
        LOG.debug(_("%s") % message)

    def deploy(self, ctxt, assembly_id, image_id):
        message = ("Deploy %s %s" % (assembly_id, image_id))
        LOG.debug(_("%s") % message)
