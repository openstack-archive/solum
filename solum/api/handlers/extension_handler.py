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


class ExtensionHandler(handler.Handler):
    """Fulfills a request on the extension resource."""

    def get(self, id):
        """Return this extension."""
        return objects.registry.Extension.get_by_uuid(self.context, id)

    def update(self, id, data):
        """Modify the extension."""
        db_obj = objects.registry.Extension.get_by_uuid(self.context, id)
        db_obj.update(data)
        db_obj.save(self.context)
        return db_obj

    def delete(self, id):
        """Delete the extension."""
        db_obj = objects.registry.Extension.get_by_uuid(self.context, id)
        db_obj.destroy(self.context)

    def create(self, data):
        """Create a new extension."""
        db_obj = objects.registry.Extension()
        db_obj.update(data)
        db_obj.uuid = str(uuid.uuid4())
        db_obj.user_id = self.context.user
        db_obj.project_id = self.context.tenant
        db_obj.create(self.context)
        return db_obj

    def get_all(self):
        """Return all operations."""
        return objects.registry.ExtensionList.get_all(self.context)
