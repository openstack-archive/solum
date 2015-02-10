# Copyright 2014 - Rackspace Hosting
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from solum.api.handlers import handler
from solum import objects
from solum.openstack.common import log as logging


LOG = logging.getLogger(__name__)


class UserlogHandler(handler.Handler):

    def get_all(self):
        """Return all userlogs, based on the query provided."""
        return objects.registry.UserlogList.get_all(self.context)

    def get_all_by_id(self, resource_uuid):
        return objects.registry.UserlogList.get_all_by_id(
            self.context, resource_uuid=resource_uuid)
