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


from solum.api.controllers.v1.datamodel import extension as model
from solum.api.controllers.v1 import extension as controller
from solum.common import exception
from solum import objects
from solum.tests import base
from solum.tests import fakes


@mock.patch('solum.common.policy.check')
@mock.patch('pecan.request', new_callable=fakes.FakePecanRequest)
@mock.patch('pecan.response', new_callable=fakes.FakePecanResponse)
@mock.patch('solum.api.controllers.v1.extension.extension_handler.'
            'ExtensionHandler')
class TestExtensionController(base.BaseTestCase):
    def setUp(self):
        super(TestExtensionController, self).setUp()
        objects.load()

    def test_extension_get(self, handler_mock, resp_mock,
                           request_mock, mock_policy):
        mock_policy.return_value = True
        handler_get = handler_mock.return_value.get
        fake_extension = fakes.FakeExtension()
        handler_get.return_value = fake_extension
        obj = controller.ExtensionController('test_id')
        result = obj.get()
        self.assertIsNotNone(result)
        self.assertEqual(fake_extension.name, result['result'].name)
        self.assertEqual(fake_extension.documentation,
                         result['result'].documentation)
        self.assertEqual(fake_extension.description,
                         result['result'].description)
        self.assertEqual(fake_extension.project_id,
                         result['result'].project_id)
        self.assertEqual(fake_extension.uuid, result['result'].uuid)
        self.assertEqual(fake_extension.version, result['result'].version)
        self.assertEqual(200, resp_mock.status)
        self.assertIsNotNone(result)
        handler_get.assert_called_once_with('test_id')

    def test_extension_get_not_found(self, handler_mock, resp_mock,
                                     request_mock, mock_policy):
        mock_policy.return_value = True
        handler_get = handler_mock.return_value.get
        handler_get.side_effect = exception.ResourceNotFound(
            name='extension', extension_id='test_id')
        obj = controller.ExtensionController('test_id')
        obj.get()
        self.assertEqual(404, resp_mock.status)
        handler_get.assert_called_once_with('test_id')

    def test_extension_put(self, handler_mock, resp_mock,
                           request_mock, mock_policy):
        json_update = {'description': 'foo_updated',
                       'user_id': 'user_id_changed',
                       'project_id': 'project_id_changed',
                       'version': '12.1',
                       'name': 'changed'}
        mock_policy.return_value = True
        request_mock.body = json.dumps(json_update)
        request_mock.content_type = 'application/json'
        handler_update = handler_mock.return_value.update
        handler_update.return_value = fakes.FakeExtension()
        obj = controller.ExtensionController('test_id')
        obj.put(fakes.FakeExtension())
        self.assertEqual(200, resp_mock.status)
        handler_update.assert_called_once_with('test_id', json_update)

    def test_extension_put_none(self, handler_mock, resp_mock,
                                request_mock, mock_policy):
        mock_policy.return_value = True
        request_mock.body = None
        request_mock.content_type = 'application/json'
        handler_put = handler_mock.return_value.put
        handler_put.return_value = fakes.FakeExtension()
        controller.ExtensionController('test_id').put()
        self.assertEqual(400, resp_mock.status)

    def test_extension_put_not_found(self, handler_mock, resp_mock,
                                     request_mock, mock_policy):
        mock_policy.return_value = True
        json_update = {'name': 'test_not_found'}
        request_mock.body = json.dumps(json_update)
        request_mock.content_type = 'application/json'
        handler_update = handler_mock.return_value.update
        handler_update.side_effect = exception.ResourceNotFound(
            name='extension', extension_id='test_id')
        controller.ExtensionController('test_id').put()
        handler_update.assert_called_with('test_id', json_update)
        self.assertEqual(404, resp_mock.status)

    def test_extension_delete(self, mock_handler, resp_mock,
                              request_mock, mock_policy):
        mock_policy.return_value = True
        handler_delete = mock_handler.return_value.delete
        handler_delete.return_value = None
        obj = controller.ExtensionController('test_id')
        obj.delete()
        handler_delete.assert_called_with('test_id')
        self.assertEqual(204, resp_mock.status)

    def test_extension_delete_not_found(self, mock_handler, resp_mock,
                                        request_mock, mock_policy):
        mock_policy.return_value = True
        handler_delete = mock_handler.return_value.delete
        handler_delete.side_effect = exception.ResourceNotFound(
            name='extension', extension_id='test_id')
        obj = controller.ExtensionController('test_id')
        obj.delete()
        handler_delete.assert_called_with('test_id')
        self.assertEqual(404, resp_mock.status)


@mock.patch('solum.common.policy.check')
@mock.patch('pecan.request', new_callable=fakes.FakePecanRequest)
@mock.patch('pecan.response', new_callable=fakes.FakePecanResponse)
@mock.patch('solum.api.controllers.v1.extension.extension_handler.'
            'ExtensionHandler')
class TestExtensionsController(base.BaseTestCase):
    def setUp(self):
        super(TestExtensionsController, self).setUp()
        objects.load()

    def test_extensions_get_all(self, handler_mock, resp_mock,
                                request_mock, mock_policy):
        mock_policy.return_value = True
        hand_get_all = handler_mock.return_value.get_all
        fake_extension = fakes.FakeExtension()
        hand_get_all.return_value = [fake_extension]
        obj = controller.ExtensionsController()
        resp = obj.get_all()
        self.assertIsNotNone(resp)
        self.assertEqual(fake_extension.name, resp['result'][0].name)
        self.assertEqual(fake_extension.documentation,
                         resp['result'][0].documentation)
        self.assertEqual(fake_extension.description,
                         resp['result'][0].description)
        self.assertEqual(fake_extension.project_id,
                         resp['result'][0].project_id)
        self.assertEqual(fake_extension.uuid, resp['result'][0].uuid)
        self.assertEqual(fake_extension.version, resp['result'][0].version)
        hand_get_all.assert_called_with()
        self.assertEqual(200, resp_mock.status)

    def test_extensions_post(self, handler_mock, resp_mock,
                             request_mock, mock_policy):
        mock_policy.return_value = True
        json_update = {'name': 'foo',
                       'description': 'foofoo',
                       'user_id': 'user_id_test',
                       'project_id': 'project_id_test',
                       'version': '1.3'}
        request_mock.body = json.dumps(json_update)
        request_mock.content_type = 'application/json'
        handler_create = handler_mock.return_value.create
        handler_create.return_value = fakes.FakeExtension()
        obj = controller.ExtensionsController()
        obj.post(fakes.FakeExtension())
        self.assertEqual(201, resp_mock.status)
        handler_create.assert_called_once_with(json_update)

    def test_extensions_post_nodata(self, handler_mock,
                                    resp_mock, request_mock, mock_policy):
        mock_policy.return_value = True
        request_mock.body = ''
        request_mock.content_type = 'application/json'
        handler_create = handler_mock.return_value.create
        handler_create.return_value = fakes.FakeExtension()
        ret_val = controller.ExtensionsController().post()
        self.assertEqual("Missing argument: \"data\"",
                         str(ret_val['faultstring']))
        self.assertEqual(400, resp_mock.status)


class TestExtensionAsDict(base.BaseTestCase):

    scenarios = [
        ('none', dict(data=None)),
        ('empty', dict(data={})),
        ('one', dict(data={'name': 'foo'})),
        ('full', dict(data={'name': 'foo',
                            'description': 'foofoo',
                            'user_id': 'user_id_test',
                            'project_id': 'project_id_test',
                            'version': '1.3'}))
    ]

    def test_as_dict(self):
        objects.load()
        if self.data is None:
            s = model.Extension()
            self.data = {}
        else:
            s = model.Extension(**self.data)
        self.data.pop('uri', None)
        self.data.pop('type', None)
        self.assertEqual(self.data, s.as_dict(objects.registry.Extension))
