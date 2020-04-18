# Copyright 2014 - Numergy
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
from unittest import mock


from solum.api.controllers.v1.datamodel import infrastructure as inframodel
from solum.api.controllers.v1 import infrastructure
from solum.common import exception
from solum import objects
from solum.tests import base
from solum.tests import fakes


@mock.patch('pecan.request', new_callable=fakes.FakePecanRequest)
@mock.patch('pecan.response', new_callable=fakes.FakePecanResponse)
class TestInfrastructureController(base.BaseTestCase):

    def test_stack_get(self, resp_mock, request_mock):
        cont = infrastructure.InfrastructureController()
        res = cont.index()
        self.assertIsNotNone(res)
        self.assertEqual(res['result'].uri, "http://test_url:8080/test/v1")
        self.assertEqual(res['result'].name, "solum")
        self.assertEqual(res['result'].type, "infrastructure")
        self.assertEqual(res['result'].description,
                         "solum infrastructure endpoint")
        self.assertEqual(res['result'].stacks_uri,
                         "http://test_url:8080/test/v1/infrastructure/stacks")


@mock.patch('pecan.request', new_callable=fakes.FakePecanRequest)
@mock.patch('pecan.response', new_callable=fakes.FakePecanResponse)
@mock.patch('solum.api.handlers.infrastructure_handler.'
            'InfrastructureStackHandler')
class TestInfrastructureStackController(base.BaseTestCase):

    def setUp(self):
        super(TestInfrastructureStackController, self).setUp()
        objects.load()

    def test_stack_get(self, StackHandler, resp_mock, request_mock):
        hand_get = StackHandler.return_value.get
        fake_stack = fakes.FakeInfrastructureStack()
        hand_get.return_value = fake_stack
        cont = infrastructure.InfrastructureStackController('test_id')
        resp = cont.get()
        self.assertIsNotNone(resp)
        self.assertEqual(fake_stack.name, resp['result'].name)
        self.assertEqual(fake_stack.image_id, resp['result'].image_id)
        self.assertEqual(fake_stack.heat_stack_id,
                         resp['result'].heat_stack_id)
        self.assertEqual(fake_stack.description,
                         resp['result'].description)
        self.assertEqual(fake_stack.project_id, resp['result'].project_id)
        self.assertEqual(fake_stack.uuid, resp['result'].uuid)
        hand_get.assert_called_with('test_id')
        self.assertEqual(200, resp_mock.status)

    def test_stack_get_not_found(self, StackHandler, resp_mock,
                                 request_mock):
        hand_get = StackHandler.return_value.get
        hand_get.side_effect = exception.ResourceNotFound(
            id='test_id', name='stack')
        cont = infrastructure.InfrastructureStackController('test_id')
        cont.get()
        hand_get.assert_called_with('test_id')
        self.assertEqual(404, resp_mock.status)

    def test_stack_put_none(self, StackHandler, resp_mock,
                            request_mock):
        request_mock.body = None
        request_mock.content_type = 'application/json'
        hand_put = StackHandler.return_value.put
        hand_put.return_value = fakes.FakeInfrastructureStack()
        infrastructure.InfrastructureStackController('test_id').put()
        self.assertEqual(400, resp_mock.status)

    def test_stack_put_not_found(self, StackHandler, resp_mock,
                                 request_mock):
        json_update = {'name': 'foo'}
        request_mock.body = json.dumps(json_update)
        request_mock.content_type = 'application/json'
        hand_update = StackHandler.return_value.update
        hand_update.side_effect = exception.ResourceNotFound(
            id='test_id', name='stack')
        infrastructure.InfrastructureStackController('test_id').put()
        hand_update.assert_called_with('test_id', json_update)
        self.assertEqual(404, resp_mock.status)

    def test_stack_put_ok(self, StackHandler, resp_mock,
                          request_mock):
        json_update = {'name': 'foo'}
        request_mock.body = json.dumps(json_update)
        request_mock.content_type = 'application/json'
        hand_update = StackHandler.return_value.update
        hand_update.return_value = fakes.FakeInfrastructureStack()
        infrastructure.InfrastructureStackController('test_id').put()
        hand_update.assert_called_with('test_id', json_update)
        self.assertEqual(200, resp_mock.status)

    def test_stack_delete_not_found(self, StackHandler,
                                    resp_mock, request_mock):
        hand_delete = StackHandler.return_value.delete
        hand_delete.side_effect = exception.ResourceNotFound(
            id='test_id', name='stack')
        obj = infrastructure.InfrastructureStackController('test_id')
        obj.delete()
        hand_delete.assert_called_with('test_id')
        self.assertEqual(404, resp_mock.status)

    def test_stack_delete_ok(self, StackHandler, resp_mock,
                             request_mock):
        hand_delete = StackHandler.return_value.delete
        hand_delete.return_value = None
        obj = infrastructure.InfrastructureStackController('test_id')
        obj.delete()
        hand_delete.assert_called_with('test_id')
        self.assertEqual(204, resp_mock.status)


@mock.patch('pecan.request', new_callable=fakes.FakePecanRequest)
@mock.patch('pecan.response', new_callable=fakes.FakePecanResponse)
@mock.patch('solum.api.handlers.infrastructure_handler.'
            'InfrastructureStackHandler')
class TestStacksController(base.BaseTestCase):
    def setUp(self):
        super(TestStacksController, self).setUp()
        objects.load()

    def test_stacks_get_all(self, handler_mock, resp_mock, request_mock):
        hand_get_all = handler_mock.return_value.get_all
        fake_stack = fakes.FakeInfrastructureStack()
        hand_get_all.return_value = [fake_stack]
        obj = infrastructure.InfrastructureStacksController()
        resp = obj.get_all()
        self.assertIsNotNone(resp)
        self.assertEqual(fake_stack.name, resp['result'][0].name)
        self.assertEqual(fake_stack.image_id, resp['result'][0].image_id)
        self.assertEqual(fake_stack.heat_stack_id,
                         resp['result'][0].heat_stack_id)
        self.assertEqual(fake_stack.description,
                         resp['result'][0].description)
        self.assertEqual(fake_stack.project_id,
                         resp['result'][0].project_id)
        self.assertEqual(fake_stack.uuid, resp['result'][0].uuid)
        self.assertEqual(200, resp_mock.status)

    def test_stacks_post(self, handler_mock, resp_mock, request_mock):
        json_create = {'name': 'foo',
                       'description': 'test_desc_stack',
                       'user_id': 'user_id_test',
                       'project_id': 'project_id_test'}
        request_mock.body = json.dumps(json_create)
        request_mock.content_type = 'application/json'
        handler_create = handler_mock.return_value.create
        handler_create.return_value = fakes.FakeInfrastructureStack()
        infrastructure.InfrastructureStacksController().post()
        handler_create.assert_called_with(json_create)
        self.assertEqual(201, resp_mock.status)
        handler_create.assert_called_once_with(json_create)

    def test_stacks_post_nodata(self, handler_mock,
                                resp_mock, request_mock):
        request_mock.body = ''
        request_mock.content_type = 'application/json'
        handler_create = handler_mock.return_value.create
        handler_create.return_value = fakes.FakeComponent()
        ret_val = infrastructure.InfrastructureStacksController().post()
        self.assertEqual("Missing argument: \"data\"",
                         str(ret_val['faultstring']))
        self.assertEqual(400, resp_mock.status)


class TestStackAsDict(base.BaseTestCase):

    scenarios = [
        ('none', dict(data=None)),
        ('one', dict(data={'name': 'foo'})),
        ('full', dict(data={'uri': 'http://example.com/v1/infrastructure/'
                                   'stack/x1',
                            'name': 'Example-stack',
                            'type': 'infrastructure_stack',
                            'project_id': '1dae5a09ef2b4d8cbf3594b0eb4f6b94',
                            'user_id': '55f41cf46df74320b9486a35f5d28a11',
                            'image_id': '1234',
                            'heat_stack_id': '5678'}))
    ]

    def test_as_dict(self):
        objects.load()
        if self.data is None:
            s = inframodel.InfrastructureStack()
            self.data = {}
        else:
            s = inframodel.InfrastructureStack(**self.data)
        if 'uri' in self.data:
            del self.data['uri']
        if 'type' in self.data:
            del self.data['type']
        self.assertEqual(self.data, s.as_dict(
            objects.registry.InfrastructureStack))
