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

import json
import mock
import testscenarios

from solum.api.controllers.v1.datamodel import plan as planmodel
from solum.api.controllers.v1 import plan
from solum.common import exception
from solum import objects
from solum.tests import base
from solum.tests import fakes


load_tests = testscenarios.load_tests_apply_scenarios


@mock.patch('pecan.request', new_callable=fakes.FakePecanRequest)
@mock.patch('pecan.response', new_callable=fakes.FakePecanResponse)
@mock.patch('solum.api.handlers.plan_handler.PlanHandler')
class TestPlanController(base.BaseTestCase):
    def setUp(self):
        super(TestPlanController, self).setUp()
        objects.load()

    def test_plan_get(self, PlanHandler, resp_mock, request_mock):
        hand_get = PlanHandler.return_value.get
        hand_get.return_value = fakes.FakePlan()
        cont = plan.PlanController('test_id')
        cont.get()
        hand_get.assert_called_with('test_id')
        self.assertEqual(200, resp_mock.status)

    def test_plan_get_not_found(self, PlanHandler, resp_mock, request_mock):
        hand_get = PlanHandler.return_value.get
        hand_get.side_effect = exception.NotFound(name='plan',
                                                  plan_id='test_id')
        cont = plan.PlanController('test_id')
        cont.get()
        hand_get.assert_called_with('test_id')
        self.assertEqual(404, resp_mock.status)

    def test_plan_put_none(self, PlanHandler, resp_mock, request_mock):
        request_mock.body = None
        request_mock.content_type = 'application/json'
        hand_put = PlanHandler.return_value.put
        hand_put.return_value = fakes.FakePlan()
        plan.PlanController('test_id').put()
        self.assertEqual(400, resp_mock.status)

    def test_plan_put_not_found(self, PlanHandler, resp_mock, request_mock):
        json_update = {'name': 'foo'}
        request_mock.body = json.dumps(json_update)
        request_mock.content_type = 'application/json'
        hand_update = PlanHandler.return_value.update
        hand_update.side_effect = exception.NotFound(name='plan',
                                                     plan_id='test_id')
        plan.PlanController('test_id').put()
        hand_update.assert_called_with('test_id', json_update)
        self.assertEqual(404, resp_mock.status)

    def test_plan_put_ok(self, PlanHandler, resp_mock, request_mock):
        json_update = {'name': 'foo'}
        request_mock.body = json.dumps(json_update)
        request_mock.content_type = 'application/json'
        hand_update = PlanHandler.return_value.update
        hand_update.return_value = fakes.FakePlan()
        plan.PlanController('test_id').put()
        hand_update.assert_called_with('test_id', json_update)
        self.assertEqual(200, resp_mock.status)

    def test_plan_delete_not_found(self, PlanHandler, resp_mock, request_mock):
        hand_delete = PlanHandler.return_value.delete
        hand_delete.side_effect = exception.NotFound(name='plan',
                                                     plan_id='test_id')
        obj = plan.PlanController('test_id')
        obj.delete()
        hand_delete.assert_called_with('test_id')
        self.assertEqual(404, resp_mock.status)

    def test_plan_delete_ok(self, PlanHandler, resp_mock, request_mock):
        hand_delete = PlanHandler.return_value.delete
        hand_delete.return_value = None
        obj = plan.PlanController('test_id')
        obj.delete()
        hand_delete.assert_called_with('test_id')
        self.assertEqual(204, resp_mock.status)


@mock.patch('pecan.request', new_callable=fakes.FakePecanRequest)
@mock.patch('pecan.response', new_callable=fakes.FakePecanResponse)
@mock.patch('solum.api.handlers.plan_handler.PlanHandler')
class TestPlansController(base.BaseTestCase):
    def setUp(self):
        super(TestPlansController, self).setUp()
        objects.load()

    def test_plans_get_all(self, PlanHandler, resp_mock, request_mock):
        hand_get = PlanHandler.return_value.get_all
        hand_get.return_value = []
        resp = plan.PlansController().get_all()
        self.assertIsNotNone(resp)
        self.assertEqual(200, resp_mock.status)
        hand_get.assert_called_with()

    def test_plans_post(self, PlanHandler, resp_mock, request_mock):
        json_update = {'name': 'foo'}
        request_mock.body = json.dumps(json_update)
        request_mock.content_type = 'application/json'
        hand_create = PlanHandler.return_value.create
        hand_create.return_value = fakes.FakePlan()
        plan.PlansController().post()
        hand_create.assert_called_with(json_update)
        self.assertEqual(201, resp_mock.status)


class TestPlanAsDict(base.BaseTestCase):

    scenarios = [
        ('none', dict(data=None)),
        ('one', dict(data={'name': 'foo'})),
        ('full', dict(data={'uri': 'http://example.com/v1/plans/x1',
                            'name': 'Example plan',
                            'type': 'plan',
                            'project_id': '1dae5a09ef2b4d8cbf3594b0eb4f6b94',
                            'user_id': '55f41cf46df74320b9486a35f5d28a11'}))
    ]

    def test_as_dict(self):
        objects.load()
        if self.data is None:
            s = planmodel.Plan()
            self.data = {}
        else:
            s = planmodel.Plan(**self.data)
        if 'uri' in self.data:
            del self.data['uri']
        if 'type' in self.data:
            del self.data['type']

        self.assertEqual(self.data, s.as_dict(objects.registry.Plan))
