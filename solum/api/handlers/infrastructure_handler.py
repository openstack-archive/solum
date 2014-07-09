# Copyright 2014 - Numergy
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

import uuid

from solum.api.handlers import handler
from solum import objects
from solum.openstack.common import log as logging


LOG = logging.getLogger(__name__)


class InfrastructureStackHandler(handler.Handler):
    """Fulfills a request on the infrastructure stack resource."""

    def get(self, id):
        """Return a stack."""
        return objects.registry.InfrastructureStack.get_by_uuid(
            self.context, id)

    def update(self, id, data):
        """Modify a stack."""
        db_obj = objects.registry.InfrastructureStack.get_by_uuid(
            self.context, id)
        db_obj.update(data)
        db_obj.save(self.context)
        return db_obj

    def delete(self, id):
        """Delete a stack."""
        db_obj = objects.registry.InfrastructureStack.get_by_uuid(
            self.context, id)
        db_obj.destroy(self.context)

    def create(self, data):
        """Create a new stack."""
        db_obj = objects.registry.InfrastructureStack()
        db_obj.update(data)
        db_obj.uuid = str(uuid.uuid4())
        db_obj.user_id = self.context.user
        db_obj.project_id = self.context.tenant
        db_obj.create(self.context)
        return db_obj

    def get_all(self):
        """Return all stacks, based on the query provided."""
        return objects.registry.InfrastructureStackList.get_all(self.context)
