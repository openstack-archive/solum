# Copyright 2013 - Rackspace
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


class AssemblyHandler(handler.Handler):
    """Fulfills a request on the assembly resource."""

    def get(self, id):
        """Return an assembly."""
        return objects.registry.Assembly.get_by_uuid(None, id)

    def trigger_workflow(self, trigger_id):
        """Get trigger by trigger id and start git worflow associated."""
        # Note: self.context will be None at this point as this is a
        # non-authenticated request.
        pass
        # Here, call a service which will trigger git workflow

    def _update_db_object(self, db_obj, data):
        for dk, dv in iter(data.items()):
            if dk == 'type':
                continue
            elif hasattr(db_obj, dk):
                setattr(db_obj, dk, dv)

    def update(self, id, data):
        """Modify a resource."""
        db_obj = objects.registry.Assembly.get_by_uuid(None, id)
        self._update_db_object(db_obj, data)
        db_obj.save(None)
        return db_obj

    def delete(self, id):
        """Delete a resource."""
        db_obj = objects.registry.Assembly.get_by_uuid(None, id)
        db_obj.destroy(None)

    def create(self, data):
        """Create a new resource."""
        db_obj = objects.registry.Assembly()
        self._update_db_object(db_obj, data)
        db_obj.uuid = str(uuid.uuid4())
        db_obj.trigger_id = str(uuid.uuid4())
        db_obj.create(None)
        return db_obj

    def get_all(self):
        """Return all assemblies, based on the query provided."""
        return objects.registry.AssemblyList.get_all(None)
