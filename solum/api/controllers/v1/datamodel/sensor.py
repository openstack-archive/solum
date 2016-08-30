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

from wsme import types as wtypes

from solum.api.controllers import common_types
from solum.api.controllers.v1.datamodel import operation
from solum.api.controllers.v1.datamodel import types as api_types
from solum.i18n import _


SENSOR_TYPE = wtypes.Enum(str, 'str', 'float', 'int')


class Sensor(api_types.Base):
    """A Sensor resource represents exactly one supported sensor.

    Sensor resources represent dynamic data about resources,
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

    timestamp = datetime.datetime
    "Timestamp for Sensor."

    operations = [operation.Operation]
    "Operations that belong to the sensor."

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

    def __init__(self, **kwds):
        self._value = '0'
        super(Sensor, self).__init__(**kwds)

    @classmethod
    def sample(cls):
        return cls(uri='http://example.com/v1/sensors/hb',
                   name='hb',
                   type='sensor',
                   project_id='1dae5a09ef2b4d8cbf3594b0eb4f6b94',
                   user_id='55f41cf46df74320b9486a35f5d28a11',
                   description='A heartbeat sensor',
                   documentation='http://example.com/docs/heartbeat/',
                   target_resource='http://example.com/instances/uuid',
                   sensor_type='str',
                   value='30',
                   timestamp=datetime.datetime.utcnow(),
                   operations=[])
