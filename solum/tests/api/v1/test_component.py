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
import mock
import testscenarios

from solum.api.controllers.v1 import component
from solum.api.controllers.v1.datamodel import component as componentmodel
from solum.common import exception
from solum import objects
from solum.tests import base
from solum.tests import fakes


load_tests = testscenarios.load_tests_apply_scenarios


@mock.patch('pecan.request', new_callable=fakes.FakePecanRequest)
@mock.patch('pecan.response', new_callable=fakes.FakePecanResponse)
@mock.patch('solum.api.handlers.component_handler.ComponentHandler')
class TestComponentController(base.BaseTestCase):
    def test_component_get(self, ComponentHandler, resp_mock, request_mock):
        hand_get = ComponentHandler.return_value.get
        hand_get.return_value = fakes.FakeComponent()
        obj = component.ComponentController('test_id')
        obj.get()
        hand_get.assert_called_with('test_id')
        self.assertEqual(200, resp_mock.status)

    def test_component_get_not_found(self, ComponentHandler,
                                     resp_mock, request_mock):
        hand_get = ComponentHandler.return_value.get
        hand_get.side_effect = exception.NotFound(name='component',
                                                  component_id='test_id')
        cont = component.ComponentController('test_id')
        cont.get()
        hand_get.assert_called_with('test_id')
        self.assertEqual(404, resp_mock.status)

    def test_component_put_none(self, ComponentHandler,
                                resp_mock, request_mock):
        request_mock.body = None
        request_mock.content_type = 'application/json'
        hand_put = ComponentHandler.return_value.put
        hand_put.return_value = fakes.FakeComponent()
        component.ComponentController('test_id').put()
        self.assertEqual(400, resp_mock.status)

    def test_component_put_not_found(self, ComponentHandler,
                                     resp_mock, request_mock):
        json_update = {'user_id': 'foo', 'name': 'appy'}
        request_mock.body = json.dumps(json_update)
        request_mock.content_type = 'application/json'
        hand_update = ComponentHandler.return_value.update
        hand_update.side_effect = exception.NotFound(name='component',
                                                     component_id='test_id')
        component.ComponentController('test_id').put()
        hand_update.assert_called_with('test_id', json_update)
        self.assertEqual(404, resp_mock.status)

    def test_component_put_ok(self, ComponentHandler, resp_mock, request_mock):
        json_update = {'name': 'fee', 'user_id': 'me'}
        request_mock.body = json.dumps(json_update)
        request_mock.content_type = 'application/json'
        hand_update = ComponentHandler.return_value.update
        hand_update.return_value = fakes.FakeComponent()
        component.ComponentController('test_id').put()
        hand_update.assert_called_with('test_id', json_update)
        self.assertEqual(200, resp_mock.status)

    def test_component_delete_not_found(self, ComponentHandler,
                                        resp_mock, request_mock):
        hand_delete = ComponentHandler.return_value.delete
        hand_delete.side_effect = exception.NotFound(name='component',
                                                     component_id='test_id')
        obj = component.ComponentController('test_id')
        obj.delete()
        hand_delete.assert_called_with('test_id')
        self.assertEqual(404, resp_mock.status)

    def test_component_delete_ok(self, ComponentHandler,
                                 resp_mock, request_mock):
        hand_delete = ComponentHandler.return_value.delete
        hand_delete.return_value = None
        obj = component.ComponentController('test_id')
        obj.delete()
        hand_delete.assert_called_with('test_id')
        self.assertEqual(204, resp_mock.status)


class TestComponentAsDict(base.BaseTestCase):

    scenarios = [
        ('none', dict(data=None)),
        ('one', dict(data={'name': 'foo'})),
        ('full', dict(data={'uri': 'http://example.com/v1/components/x1',
                            'name': 'Example component',
                            'type': 'component',
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
