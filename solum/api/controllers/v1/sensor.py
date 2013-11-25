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

import datetime

import pecan
from pecan import rest
import wsme
from wsme import types as wtypes
import wsmeext.pecan as wsme_pecan

from solum.api.controllers import common_types


class Sensor(wtypes.Base):
    """A Sensor resource represents exactly one supported sensor on one or
    more resources. Sensor resources represent dynamic data about resources,
    such as metrics or state. Sensor resources are useful for exposing data
    that changes rapidly, or that may need to be fetched from a secondary
    system.
    """

    uri = common_types.Uri
    "Uri to the sensor"

    name = wtypes.text
    "Name of the sensor"

    type = wtypes.text
    "Sensor type"

    description = wtypes.text
    "Description of the sensor"

    documentation = common_types.Uri
    "Documentation uri for the sensor"

    targetResource = common_types.Uri
    "Target resource uri to the sensor"

    sensorType = wtypes.text
    "Sensor type"

    value = sensorType
    "Value of sensor"

    timestamp = datetime.datetime
    "Timestamp for Sensor"

    operationsUri = common_types.Uri
    "Operations uri for the sensor"

    @classmethod
    def sample(cls):
        return cls(uri='http://example.com/v1/sensors/hb',
                   name='hb',
                   type='sensor',
                   description='A heartbeat sensor',
                   documentation='http://example.com/docs/heartbeat/',
                   targetResource='http://example.com/instances/uuid',
                   sensorType='int',
                   value='30',
                   timestamp=datetime.datetime.utcnow(),
                   operationsUri='http://example.com:9777/v1/operations/stop')


class SensorController(rest.RestController):
    """Manages operations on a single sensor."""

    def __init__(self, sensor_id):
        pecan.request.context['sensor_id'] = sensor_id
        self._id = sensor_id

    @wsme_pecan.wsexpose(Sensor, wtypes.text)
    def get(self):
        """Return this sensor."""
        error = _("Not implemented")
        pecan.response.translatable_error = error
        raise wsme.exc.ClientSideError(unicode(error))

    @wsme_pecan.wsexpose(Sensor, wtypes.text, body=Sensor)
    def put(self, data):
        """Modify this sensor."""
        error = _("Not implemented")
        pecan.response.translatable_error = error
        raise wsme.exc.ClientSideError(unicode(error))

    @wsme_pecan.wsexpose(None, wtypes.text, status_code=204)
    def delete(self):
        """Delete this sensor."""
        error = _("Not implemented")
        pecan.response.translatable_error = error
        raise wsme.exc.ClientSideError(unicode(error))


class Sensors(wtypes.Base):
    """A collection of sensors returned on listing."""

    uri = common_types.Uri
    "Uri to the Sensors"

    name = wtypes.text
    "Name of the sensor"

    type = wtypes.text
    "Sensor type"

    description = wtypes.text
    "Description of the sensor"

    targetResource = common_types.Uri
    "Target resource uri to the sensor"

    sensorLinks = [common_types.Link]
    "List of links to the available sensors"

    @classmethod
    def sample(cls):
        return cls(uri='http://example.com/v1/sensors',
                   sensorLinks=[common_types.Link(
                       href='http://example.com:9777/v1/sensors/y4',
                       targetName='y4')])


class SensorsController(rest.RestController):
    """Manages operations on the sensors collection."""

    @pecan.expose()
    def _lookup(self, sensor_id, *remainder):
        if remainder and not remainder[-1]:
            remainder = remainder[:-1]
        return SensorController(sensor_id), remainder

    @wsme_pecan.wsexpose(Sensor, body=Sensor, status_code=201)
    def post(self, data):
        """Create a new sensor."""
        error = _("Not implemented")
        pecan.response.translatable_error = error
        raise wsme.exc.ClientSideError(unicode(error))

    @wsme_pecan.wsexpose(Sensors)
    def get_all(self):
        """Return all sensors, based on the query provided."""
        host_url = '/'.join([pecan.request.host_url, 'v1', 'sensors'])
        return Sensors(uri=host_url,
                       type='sensors',
                       description='Collection of sensors',
                       sensorLinks=[])
