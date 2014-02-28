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


class SensorHandler(handler.Handler):
    """Fulfills a request on the sensor resource."""

    def __init__(self):
        super(SensorHandler, self).__init__()

    def get(self, id):
        """Return a sensor."""
        return objects.registry.Sensor.get_by_uuid(None, id)

    def _update_db_object(self, db_obj, data):
        filtered_keys = set(('id', 'uuid', 'uri', 'type'))
        for field in set(six.iterkeys(data)) - filtered_keys:
            setattr(db_obj, field, data[field])

    def update(self, id, data):
        """Modify the sensor."""
        db_obj = objects.registry.Sensor.get_by_uuid(None, id)
        self._update_db_object(db_obj, data)
        db_obj.save(None)
        return db_obj

    def delete(self, id):
        """Delete the sensor."""
        db_obj = objects.registry.Sensor.get_by_uuid(None, id)
        db_obj.delete()

    def create(self, data):
        """Create a new sensor."""
        db_obj = objects.registry.Sensor()
        self._update_db_object(db_obj, data)
        db_obj.uuid = str(uuid.uuid4())
        db_obj.create()
        return db_obj

    def get_all(self):
        """Return all sensors."""
        return objects.registry.SensorList.get_all(None)
