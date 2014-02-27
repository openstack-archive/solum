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

from solum.api.controllers.v1 import plan
from solum.tests import base
from solum.tests import fakes


@mock.patch('pecan.request', new_callable=fakes.FakePecanRequest)
@mock.patch('pecan.response', new_callable=fakes.FakePecanResponse)
class TestPlanController(base.BaseTestCase):
    def test_plan_get(self, resp_mock, request_mock):
        plan_obj = plan.PlanController('test_id')
        plan_obj.get()
        self.assertEqual(200, resp_mock.status)

    def test_plan_put(self, resp_mock, request_mock):
        obj = plan.PlanController('test_id')
        obj.put(None)
        self.assertEqual(501, resp_mock.status)

    def test_plan_delete(self, resp_mock, request_mock):
        obj = plan.PlanController('test_id')
        obj.delete()
        self.assertEqual(501, resp_mock.status)


@mock.patch('pecan.request', new_callable=fakes.FakePecanRequest)
@mock.patch('pecan.response', new_callable=fakes.FakePecanResponse)
class TestPlansController(base.BaseTestCase):
    def test_plans_get_all(self, resp_mock, request_mock):
        plans_obj = plan.PlansController()
        resp = plans_obj.get_all()
        self.assertIsNotNone(resp)
        self.assertEqual(200, resp_mock.status)

    def test_plans_post(self, resp_mock, request_mock):
        plans_obj = plan.PlansController()
        plans_obj.post(None)
        self.assertEqual(501, resp_mock.status)
