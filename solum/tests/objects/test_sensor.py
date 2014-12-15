# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from solum.objects import registry
from solum.objects.sqlalchemy import sensor
from solum.tests import base
from solum.tests import utils


class TestSensor(base.BaseTestCase):
    def setUp(self):
        super(TestSensor, self).setUp()
        self.db = self.useFixture(utils.Database())
        self.ctx = utils.dummy_context()

        self.data = [{'uuid': 'test-uuid-34dsxD',
                      'project_id': self.ctx.tenant,
                      'user_id': '55f41cf46df74320b9486a35f5d28a11',
                      'name': 'hb',
                      'description': 'A heartbeat sensor',
                      'documentation': 'http://example.com/docs/heartbeat/',
                      'target_resource': 'http://example.com/instances/uuid',
                      'sensor_type': 'str',
                      'value': '30'}]
        utils.create_models_from_data(sensor.Sensor,
                                      self.data, self.ctx)

    def test_objects_registered(self):
        self.assertTrue(registry.Sensor)
        self.assertTrue(registry.SensorList)

    def test_get_all(self):
        lst = sensor.SensorList()
        self.assertEqual(1, len(lst.get_all(self.ctx)))

    def test_check_data_by_id(self):
        s = sensor.Sensor().get_by_id(self.ctx, self.data[0]['id'])
        self.assertIsNotNone(s)
        for key, value in self.data[0].items():
            self.assertEqual(value, getattr(s, key))

    def test_check_data_by_uuid(self):
        s = sensor.Sensor().get_by_uuid(self.ctx, self.data[0]['uuid'])
        self.assertIsNotNone(s)
        for key, value in self.data[0].items():
            self.assertEqual(value, getattr(s, key))
