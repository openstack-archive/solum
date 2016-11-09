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

from oslo_utils import uuidutils

from solum.api.handlers import handler
from solum import objects


class OperationHandler(handler.Handler):
    """Fulfills a request on the operation resource."""

    def get(self, uuid):
        """Return this operation."""
        return objects.registry.Operation.get_by_uuid(self.context, uuid)

    def update(self, uuid, data):
        """Modify the operation."""
        updated = objects.registry.Operation.update_and_save(self.context,
                                                             uuid, data)
        return updated

    def delete(self, uuid):
        """Delete the operation."""
        db_obj = objects.registry.Operation.get_by_uuid(self.context, uuid)
        db_obj.destroy(self.context)

    def create(self, data):
        """Create a new operation."""
        db_obj = objects.registry.Operation()
        db_obj.update(data)
        db_obj.uuid = uuidutils.generate_uuid()
        db_obj.create(self.context)
        return db_obj

    def get_all(self):
        """Return all operations."""
        return objects.registry.OperationList.get_all(self.context)
