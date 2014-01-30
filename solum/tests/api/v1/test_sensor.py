# Copyright 2013 - Red Hat, Inc.
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
import testscenarios

from solum.api.controllers.v1.datamodel import sensor as model
from solum.api.controllers.v1 import sensor as controller
from solum.tests import base
from solum.tests import fakes


load_tests = testscenarios.load_tests_apply_scenarios


class TestSensorValueTypeGood(base.BaseTestCase):

    scenarios = [
        ('int_str', dict(
            in_value=3, in_type='str', out_value='3')),
        ('int_int', dict(
            in_value=3, in_type='int', out_value=3)),
        ('str_int', dict(
            in_value='3', in_type='int', out_value=3)),
        ('float_str', dict(
            in_value=3.4, in_type='str', out_value='3.4')),
        ('str_float', dict(
            in_value='2.45', in_type='float', out_value=2.45)),
        ('float_float', dict(
            in_value=2.45, in_type='float', out_value=2.45)),
    ]

    def test_values(self):
        s = model.Sensor(sensor_type=self.in_type, value=self.in_value)
        self.assertEqual(self.out_value, s.value)


class TestSensorValueTypeBad(base.BaseTestCase):

    scenarios = [
        ('sp_int', dict(
            in_value=3.2, in_type='int')),
        ('bp_int', dict(
            in_value=3.7, in_type='int')),
        ('sn_int', dict(
            in_value=-3.1, in_type='int')),
        ('bn_int', dict(
            in_value=-3.9, in_type='int')),
        ('float', dict(
            in_value='sunny', in_type='float')),
    ]

    def test_values(self):
        s = model.Sensor(sensor_type=self.in_type, value=self.in_value)
        self.assertRaises(ValueError, getattr, s, 'value')


@mock.patch('pecan.request', new_callable=fakes.FakePecanRequest)
@mock.patch('pecan.response', new_callable=fakes.FakePecanResponse)
class TestSensorController(base.BaseTestCase):
    def test_sensor_get(self, resp_mock, request_mock):
        obj = controller.SensorController('test_id')
        sensor_model = obj.get()
        self.assertEqual(200, resp_mock.status)
        self.assertIsNotNone(sensor_model)

    def test_sensor_put(self, resp_mock, request_mock):
        obj = controller.SensorController('test_id')
        obj.put(None)
        self.assertEqual(400, resp_mock.status)

    def test_sensor_delete(self, resp_mock, request_mock):
        obj = controller.SensorController('test_id')
        obj.delete()
        self.assertEqual(400, resp_mock.status)
