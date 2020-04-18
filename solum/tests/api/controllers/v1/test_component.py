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

import json
from unittest import mock


from solum.api.controllers.v1 import component
from solum.api.controllers.v1.datamodel import component as componentmodel
from solum.common import exception
from solum import objects
from solum.tests import base
from solum.tests import fakes


@mock.patch('solum.common.policy.check')
@mock.patch('pecan.request', new_callable=fakes.FakePecanRequest)
@mock.patch('pecan.response', new_callable=fakes.FakePecanResponse)
@mock.patch('solum.api.handlers.component_handler.ComponentHandler')
class TestComponentController(base.BaseTestCase):
    def setUp(self):
        super(TestComponentController, self).setUp()
        objects.load()

    def test_component_get(self, ComponentHandler, resp_mock,
                           request_mock, mock_policy):
        mock_policy.return_value = True
        hand_get = ComponentHandler.return_value.get
        fake_component = fakes.FakeComponent()
        hand_get.return_value = fake_component
        obj = component.ComponentController('test_id')
        resp = obj.get()
        self.assertIsNotNone(resp)
        self.assertEqual(fake_component.name, resp['result'].name)
        self.assertEqual(fake_component.description,
                         resp['result'].description)
        hand_get.assert_called_with('test_id')
        self.assertEqual(200, resp_mock.status)

    def test_component_get_not_found(self, ComponentHandler,
                                     resp_mock, request_mock, mock_policy):
        mock_policy.return_value = True
        hand_get = ComponentHandler.return_value.get
        hand_get.side_effect = exception.ResourceNotFound(
            name='component', component_id='test_id')
        cont = component.ComponentController('test_id')
        cont.get()
        hand_get.assert_called_with('test_id')
        self.assertEqual(404, resp_mock.status)

    def test_component_put_none(self, ComponentHandler,
                                resp_mock, request_mock, mock_policy):
        mock_policy.return_value = True
        request_mock.body = None
        request_mock.content_type = 'application/json'
        hand_put = ComponentHandler.return_value.put
        hand_put.return_value = fakes.FakeComponent()
        component.ComponentController('test_id').put()
        self.assertEqual(400, resp_mock.status)

    def test_component_put_not_found(self, ComponentHandler,
                                     resp_mock, request_mock, mock_policy):
        mock_policy.return_value = True
        json_update = {'user_id': 'foo', 'name': 'appy'}
        request_mock.body = json.dumps(json_update)
        request_mock.content_type = 'application/json'
        hand_update = ComponentHandler.return_value.update
        hand_update.side_effect = exception.ResourceNotFound(
            name='component', component_id='test_id')
        component.ComponentController('test_id').put()
        hand_update.assert_called_with('test_id', json_update)
        self.assertEqual(404, resp_mock.status)

    def test_component_put_ok(self, ComponentHandler, resp_mock,
                              request_mock, mock_policy):
        mock_policy.return_value = True
        json_update = {'name': 'update_foo',
                       'description': 'update_desc_component',
                       'user_id': 'user_id_test',
                       'project_id': 'project_id_test'}
        request_mock.body = json.dumps(json_update)
        request_mock.content_type = 'application/json'
        hand_update = ComponentHandler.return_value.update
        hand_update.return_value = fakes.FakeComponent()
        component.ComponentController('test_id').put()
        hand_update.assert_called_with('test_id', json_update)
        self.assertEqual(200, resp_mock.status)

    def test_component_delete_not_found(self, ComponentHandler,
                                        resp_mock, request_mock, mock_policy):
        mock_policy.return_value = True
        hand_delete = ComponentHandler.return_value.delete
        hand_delete.side_effect = exception.ResourceNotFound(
            name='component', component_id='test_id')
        obj = component.ComponentController('test_id')
        obj.delete()
        hand_delete.assert_called_with('test_id')
        self.assertEqual(404, resp_mock.status)

    def test_component_delete_ok(self, ComponentHandler,
                                 resp_mock, request_mock, mock_policy):
        mock_policy.return_value = True
        hand_delete = ComponentHandler.return_value.delete
        hand_delete.return_value = None
        obj = component.ComponentController('test_id')
        obj.delete()
        hand_delete.assert_called_with('test_id')
        self.assertEqual(204, resp_mock.status)


@mock.patch('solum.common.policy.check')
@mock.patch('pecan.request', new_callable=fakes.FakePecanRequest)
@mock.patch('pecan.response', new_callable=fakes.FakePecanResponse)
@mock.patch('solum.api.handlers.component_handler.ComponentHandler')
class TestComponentsController(base.BaseTestCase):
    def setUp(self):
        super(TestComponentsController, self).setUp()
        objects.load()

    def test_components_get_all(self, handler_mock, resp_mock,
                                request_mock, mock_policy):
        mock_policy.return_value = True
        hand_get_all = handler_mock.return_value.get_all
        fake_component = fakes.FakeComponent()
        hand_get_all.return_value = [fake_component]
        obj = component.ComponentsController()
        resp = obj.get_all()
        hand_get_all.assert_called_with()
        self.assertIsNotNone(resp)
        self.assertEqual(fake_component.name, resp['result'][0].name)
        self.assertEqual(fake_component.description,
                         resp['result'][0].description)
        self.assertEqual(200, resp_mock.status)

    def test_components_post(self, handler_mock, resp_mock,
                             request_mock, mock_policy):
        json_create = {'name': 'foo',
                       'description': 'test_desc_component',
                       'user_id': 'user_id_test',
                       'project_id': 'project_id_test'}
        mock_policy.return_value = True
        request_mock.body = json.dumps(json_create)
        request_mock.content_type = 'application/json'
        handler_create = handler_mock.return_value.create
        handler_create.return_value = fakes.FakeComponent()
        component.ComponentsController().post()
        handler_create.assert_called_with(json_create)
        self.assertEqual(201, resp_mock.status)
        handler_create.assert_called_once_with(json_create)

    def test_components_post_nodata(self, handler_mock,
                                    resp_mock, request_mock, mock_policy):
        mock_policy.return_value = True
        request_mock.body = ''
        request_mock.content_type = 'application/json'
        handler_create = handler_mock.return_value.create
        handler_create.return_value = fakes.FakeComponent()
        ret_val = component.ComponentsController().post()
        self.assertEqual("Missing argument: \"data\"",
                         str(ret_val['faultstring']))
        self.assertEqual(400, resp_mock.status)


class TestComponentAsDict(base.BaseTestCase):

    scenarios = [
        ('none', dict(data=None)),
        ('one', dict(data={'name': 'foo'})),
        ('full', dict(data={'uri': 'http://example.com/v1/components/x1',
                            'name': 'Example-component',
                            'type': 'component',
                            'component_type': 'heat_stack',
                            'tags': ['small'],
                            'project_id': '1dae5a09ef2b4d8cbf3594b0eb4f6b94',
                            'user_id': '55f41cf46df74320b9486a35f5d28a11',
                            'description': 'A component'}))
    ]

    def test_as_dict(self):
        objects.load()
        if self.data is None:
            s = componentmodel.Component()
            self.data = {}
        else:
            s = componentmodel.Component(**self.data)
        if 'uri' in self.data:
            del self.data['uri']
        if 'type' in self.data:
            del self.data['type']
        self.assertEqual(self.data,
                         s.as_dict(objects.registry.Component))
