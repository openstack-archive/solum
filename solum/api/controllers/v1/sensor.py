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
import six
import wsme
from wsme import types as wtypes
import wsmeext.pecan as wsme_pecan

from solum.api.controllers.v1.datamodel import sensor
from solum.api.handlers import sensor_handler
from solum.common import exception
from solum.openstack.common.gettextutils import _


class SensorController(rest.RestController):
    """Manages operations on a single sensor."""

    def __init__(self, sensor_id):
        pecan.request.context['sensor_id'] = sensor_id
        self._id = sensor_id

    @exception.wrap_controller_exception
    @wsme_pecan.wsexpose(sensor.Sensor, wtypes.text)
    def get(self):
        """Return this sensor."""
        handler = sensor_handler.SensorHandler()
        return handler.get(self._id)

    @wsme_pecan.wsexpose(sensor.Sensor, wtypes.text, body=sensor.Sensor)
    def put(self, data):
        """Modify this sensor."""
        error = _("Not implemented")
        pecan.response.translatable_error = error
        raise wsme.exc.ClientSideError(six.text_type(error))

    @wsme_pecan.wsexpose(None, wtypes.text, status_code=204)
    def delete(self):
        """Delete this sensor."""
        error = _("Not implemented")
        pecan.response.translatable_error = error
        raise wsme.exc.ClientSideError(six.text_type(error))


class SensorsController(rest.RestController):
    """Manages operations on the sensors collection."""

    @pecan.expose()
    def _lookup(self, sensor_id, *remainder):
        if remainder and not remainder[-1]:
            remainder = remainder[:-1]
        return SensorController(sensor_id), remainder

    @wsme_pecan.wsexpose(sensor.Sensor, body=sensor.Sensor, status_code=201)
    def post(self, data):
        """Create a new sensor."""
        error = _("Not implemented")
        pecan.response.translatable_error = error
        raise wsme.exc.ClientSideError(six.text_type(error))

    @wsme_pecan.wsexpose([sensor.Sensor])
    def get_all(self):
        """Return all sensors, based on the query provided."""
        return []
