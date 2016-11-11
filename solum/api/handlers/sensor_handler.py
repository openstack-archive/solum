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


class SensorHandler(handler.Handler):
    """Fulfills a request on the sensor resource."""

    def get(self, id):
        """Return a sensor."""
        return objects.registry.Sensor.get_by_uuid(self.context, id)

    def update(self, id, data):
        """Modify the sensor."""
        updated = objects.registry.Sensor.update_and_save(self.context,
                                                          id, data)
        return updated

    def delete(self, id):
        """Delete the sensor."""
        db_obj = objects.registry.Sensor.get_by_uuid(self.context, id)
        db_obj.destroy(self.context)

    def create(self, data):
        """Create a new sensor."""
        db_obj = objects.registry.Sensor()
        db_obj.update(data)
        db_obj.uuid = uuidutils.generate_uuid()
        db_obj.user_id = self.context.user
        db_obj.project_id = self.context.tenant
        db_obj.create(self.context)
        return db_obj

    def get_all(self):
        """Return all sensors."""
        return objects.registry.SensorList.get_all(self.context)
