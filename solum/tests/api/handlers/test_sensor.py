# -*- coding: utf-8 -*-
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

import mock

from solum.api.handlers import sensor_handler as sensor
from solum.tests import base
from solum.tests import fakes
from solum.tests import utils


@mock.patch('solum.objects.registry')
class TestSensorHandler(base.BaseTestCase):
    def setUp(self):
        super(TestSensorHandler, self).setUp()
        self.ctx = utils.dummy_context()

    def test_sensor_get(self, mock_registry):
        mock_registry.Sensor.get_by_uuid.return_value = {}
        handler = sensor.SensorHandler(self.ctx)
        res = handler.get('test_id')
        self.assertIsNotNone(res)
        mock_registry.Sensor.get_by_uuid.assert_called_once_with(None,
                                                                 'test_id')

    def test_sensor_get_all(self, mock_registry):
        mock_registry.SensorList.get_all.return_value = {}
        handler = sensor.SensorHandler(self.ctx)
        res = handler.get_all()
        self.assertIsNotNone(res)
        mock_registry.SensorList.get_all.assert_called_once_with(None)

    def test_sensor_update(self, mock_registry):
        data = {'user_id': 'new_user_id'}
        db_obj = fakes.FakeSensor()
        mock_registry.Sensor.get_by_uuid.return_value = db_obj
        handler = sensor.SensorHandler(self.ctx)
        res = handler.update('test_id', data)
        self.assertEqual(db_obj.user_id, res.user_id)
        self.assertEqual(db_obj.project_id, res.project_id)
        self.assertEqual(db_obj.name, res.name)
        self.assertEqual(db_obj.value, res.value)
        self.assertEqual(db_obj.sensor_type, res.sensor_type)
        self.assertEqual(db_obj.target_resource, res.target_resource)
        self.assertEqual(db_obj.uuid, res.uuid)
        self.assertEqual(db_obj.uri, res.uri)
        self.assertEqual(db_obj.type, res.type)
        db_obj.save.assert_called_once_with(None)
        mock_registry.Sensor.get_by_uuid.assert_called_once_with(None,
                                                                 'test_id')

    def test_sensor_create(self, mock_registry):
        data = {'user_id': 'new_user_id',
                'uuid': 'input_uuid'}
        handler = sensor.SensorHandler(self.ctx)
        res = handler.create(data)
        self.assertEqual('new_user_id', res.user_id)
        self.assertNotEqual('uuid', res.uuid)

    def test_sensor_delete(self, mock_registry):
        db_obj = fakes.FakeSensor()
        mock_registry.Sensor.get_by_uuid.return_value = db_obj
        handler = sensor.SensorHandler(self.ctx)
        handler.delete('test_id')
        db_obj.destroy.assert_called_once_with(None)
        mock_registry.Sensor.get_by_uuid.assert_called_once_with(None,
                                                                 'test_id')
