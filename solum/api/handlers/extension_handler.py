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

import six

from solum.api.handlers import handler
from solum import objects


class ExtensionHandler(handler.Handler):
    """Fulfills a request on the extension resource."""

    def __init__(self):
        super(ExtensionHandler, self).__init__()

    def get(self, id):
        """Return this extension."""
        return objects.registry.Extension.get_by_uuid(None, id)

    def _update_db_object(self, db_obj, data):
        filtered_keys = set(('id', 'uuid', 'uri', 'type'))
        for field in set(six.iterkeys(data)) - filtered_keys:
            setattr(db_obj, field, data[field])

    def update(self, id, data):
        """Modify the extension."""
        db_obj = objects.registry.Extension.get_by_uuid(None, id)
        self._update_db_object(db_obj, data)
        db_obj.save(None)
        return db_obj

    def delete(self, id):
        """Delete the extension."""
        db_obj = objects.registry.Extension.get_by_uuid(None, id)
        db_obj.delete()

    def create(self, data):
        """Create a new extension."""
        db_obj = objects.registry.Extension()
        db_obj.uuid = str(uuid.uuid4())
        self._update_db_object(db_obj, data)
        db_obj.create()
        return db_obj

    def get_all(self):
        """Return all operations."""
        return objects.registry.ExtensionList.get_all(None)
