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

import pecan
from pecan import rest
from wsme import types as wtypes
import wsmeext.pecan as wsme_pecan

from solum.api.controllers.v1.datamodel import sensor
from solum.api.handlers import sensor_handler
from solum.common import exception
from solum.common import policy
from solum import objects


class SensorController(rest.RestController):
    """Manages operations on a single sensor."""

    def __init__(self, sensor_id):
        super(SensorController, self).__init__()
        self._id = sensor_id

    @exception.wrap_wsme_pecan_controller_exception
    @wsme_pecan.wsexpose(sensor.Sensor, wtypes.text)
    def get(self):
        """Return this sensor."""
        policy.check('show_sensor',
                     pecan.request.security_context)
        handler = sensor_handler.SensorHandler(pecan.request.security_context)
        host_url = pecan.request.application_url.rstrip('/')
        return sensor.Sensor.from_db_model(handler.get(self._id), host_url)

    @exception.wrap_wsme_pecan_controller_exception
    @wsme_pecan.wsexpose(sensor.Sensor, wtypes.text, body=sensor.Sensor)
    def put(self, data):
        """Modify this sensor."""
        policy.check('update_sensor',
                     pecan.request.security_context)
        handler = sensor_handler.SensorHandler(pecan.request.security_context)
        obj = handler.update(self._id,
                             data.as_dict(objects.registry.Sensor))
        host_url = pecan.request.application_url.rstrip('/')
        return sensor.Sensor.from_db_model(obj, host_url)

    @exception.wrap_wsme_pecan_controller_exception
    @wsme_pecan.wsexpose(None, wtypes.text, status_code=204)
    def delete(self):
        """Delete this sensor."""
        policy.check('delete_sensor',
                     pecan.request.security_context)
        handler = sensor_handler.SensorHandler(pecan.request.security_context)
        handler.delete(self._id)


class SensorsController(rest.RestController):
    """Manages operations on the sensors collection."""

    @pecan.expose()
    def _lookup(self, sensor_id, *remainder):
        if remainder and not remainder[-1]:
            remainder = remainder[:-1]
        return SensorController(sensor_id), remainder

    @exception.wrap_wsme_pecan_controller_exception
    @wsme_pecan.wsexpose(sensor.Sensor, wtypes.text,
                         body=sensor.Sensor, status_code=201)
    def post(self, data):
        """Create a new sensor."""
        policy.check('create_sensor',
                     pecan.request.security_context)
        handler = sensor_handler.SensorHandler(pecan.request.security_context)
        obj = handler.create(data.as_dict(objects.registry.Sensor))
        host_url = pecan.request.application_url.rstrip('/')
        return sensor.Sensor.from_db_model(obj, host_url)

    @exception.wrap_wsme_pecan_controller_exception
    @wsme_pecan.wsexpose([sensor.Sensor])
    def get_all(self):
        """Return all sensors, based on the query provided."""
        policy.check('get_sensors',
                     pecan.request.security_context)
        handler = sensor_handler.SensorHandler(pecan.request.security_context)
        host_url = pecan.request.application_url.rstrip('/')
        return [sensor.Sensor.from_db_model(obj, host_url)
                for obj in handler.get_all()]
