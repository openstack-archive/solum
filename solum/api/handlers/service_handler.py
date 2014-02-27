# Copyright 2014 - Rackspace
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


class ServiceHandler(handler.Handler):
    """Fulfills a request on the service resource."""

    def get(self, id):
        """Return a service."""
        return objects.registry.Service.get_by_uuid(None, id)

    def _update_db_object(self, db_obj, data):
        for dk, dv in iter(data.items()):
            if dk == 'type':
                continue
            elif hasattr(db_obj, dk):
                setattr(db_obj, dk, dv)

    def update(self, id, data):
        """Modify a resource."""
        db_obj = objects.registry.Service.get_by_uuid(None, id)
        self._update_db_object(db_obj, data)
        db_obj.save(None)
        return db_obj

    def delete(self, id):
        """Delete a resource."""
        db_obj = objects.registry.Service.get_by_uuid(None, id)
        db_obj.destroy(None)

    def create(self, data):
        """Create a new resource."""
        db_obj = objects.registry.Service()
        db_obj.uuid = str(uuid.uuid4())
        self._update_db_object(db_obj, data)
        db_obj.create(None)
        return db_obj

    def get_all(self):
        """Return all services."""
        return objects.registry.ServiceList.get_all(None)
