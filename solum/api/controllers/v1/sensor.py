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

from solum.openstack.common.gettextutils import _  # noqa

from solum.api.controllers import common_types
from solum.api.controllers.v1 import types as api_types


SENSOR_TYPE = wtypes.Enum(str, 'str', 'float', 'int')


class Sensor(api_types.Base):
    """A Sensor resource represents exactly one supported sensor on one or
    more resources. Sensor resources represent dynamic data about resources,
    such as metrics or state. Sensor resources are useful for exposing data
    that changes rapidly, or that may need to be fetched from a secondary
    system.
    """

    documentation = common_types.Uri
    "Documentation URI for the sensor."

    target_resource = common_types.Uri
    "Target resource URI to the sensor."

    sensor_type = SENSOR_TYPE
    "Sensor data type."

    def get_value(self):
        if self.sensor_type == 'int':
            if int(self._value) != float(self._value):
                raise ValueError(_('Value "%s" is not an integer.') %
                                 str(self._value))
            return int(self._value)
        elif self.sensor_type == 'float':
            return float(self._value)
        else:
            return str(self._value)

    def set_value(self, value):
        # Store the value as-is, because we don't know the order that the
        # value and sensor_type are written, so convert to the desired type
        # in get_value().
        self._value = value

    value = wtypes.wsproperty(str, get_value, set_value, mandatory=False)
    "Value of the sensor."

    timestamp = datetime.datetime
    "Timestamp for Sensor."

    operations_uri = common_types.Uri
    "Operations URI for the sensor."

    def __init__(self, **kwds):
        self._value = '0'
        super(Sensor, self).__init__(**kwds)

    @classmethod
    def sample(cls):
        return cls(uri='http://example.com/v1/sensors/hb',
                   name='hb',
                   type='sensor',
                   description='A heartbeat sensor',
                   documentation='http://example.com/docs/heartbeat/',
                   target_resource='http://example.com/instances/uuid',
                   sensor_type='str',
                   value='30',
                   timestamp=datetime.datetime.utcnow(),
                   operations_uri='http://example.com:9777/operations/stop')


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

    @wsme_pecan.wsexpose([Sensor])
    def get_all(self):
        """Return all sensors, based on the query provided."""
        return []
