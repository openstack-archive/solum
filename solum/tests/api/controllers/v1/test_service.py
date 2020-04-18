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


from solum.api.controllers.v1.datamodel import service as servicemodel
from solum.api.controllers.v1 import service
from solum.common import exception
from solum import objects
from solum.tests import base
from solum.tests import fakes


@mock.patch('solum.common.policy.check')
@mock.patch('pecan.request', new_callable=fakes.FakePecanRequest)
@mock.patch('pecan.response', new_callable=fakes.FakePecanResponse)
@mock.patch('solum.api.handlers.service_handler.ServiceHandler')
class TestServiceController(base.BaseTestCase):
    def setUp(self):
        super(TestServiceController, self).setUp()
        objects.load()

    def test_service_get(self, ServiceHandler, resp_mock,
                         request_mock, mock_policy):
        mock_policy.return_value = True
        hand_get = ServiceHandler.return_value.get
        fake_service = fakes.FakeService()
        hand_get.return_value = fake_service
        cont = service.ServiceController('test_id')
        resp = cont.get()
        self.assertIsNotNone(resp)
        self.assertEqual(fake_service.name, resp['result'].name)
        self.assertEqual(fake_service.description,
                         resp['result'].description)
        self.assertEqual(fake_service.project_id, resp['result'].project_id)
        self.assertEqual(fake_service.uuid, resp['result'].uuid)
        hand_get.assert_called_with('test_id')
        self.assertEqual(200, resp_mock.status)

    def test_service_get_not_found(self, ServiceHandler,
                                   resp_mock, request_mock, mock_policy):
        mock_policy.return_value = True
        hand_get = ServiceHandler.return_value.get
        hand_get.side_effect = exception.ResourceNotFound(
            name='service', service_id='test_id')
        cont = service.ServiceController('test_id')
        cont.get()
        hand_get.assert_called_with('test_id')
        self.assertEqual(404, resp_mock.status)

    def test_service_put_none(self, ServiceHandler, resp_mock,
                              request_mock, mock_policy):
        mock_policy.return_value = True
        request_mock.body = None
        request_mock.content_type = 'application/json'
        hand_put = ServiceHandler.return_value.put
        hand_put.return_value = fakes.FakeService()
        service.ServiceController('test_id').put()
        self.assertEqual(400, resp_mock.status)

    def test_service_put_not_found(self, ServiceHandler,
                                   resp_mock, request_mock, mock_policy):
        mock_policy.return_value = True
        json_update = {'user_id': 'foo', 'name': 'appy'}
        request_mock.body = json.dumps(json_update)
        request_mock.content_type = 'application/json'
        hand_update = ServiceHandler.return_value.update
        hand_update.side_effect = exception.ResourceNotFound(
            name='service',
            service_id='test_id')
        service.ServiceController('test_id').put()
        hand_update.assert_called_with('test_id', json_update)
        self.assertEqual(404, resp_mock.status)

    def test_service_put_ok(self, ServiceHandler, resp_mock,
                            request_mock, mock_policy):
        mock_policy.return_value = True
        json_update = {'name': 'fee', 'user_id': 'me'}
        request_mock.body = json.dumps(json_update)
        request_mock.content_type = 'application/json'
        hand_update = ServiceHandler.return_value.update
        hand_update.return_value = fakes.FakeService()
        service.ServiceController('test_id').put()
        hand_update.assert_called_with('test_id', json_update)
        self.assertEqual(200, resp_mock.status)

    def test_service_delete_not_found(self, ServiceHandler,
                                      resp_mock, request_mock, mock_policy):
        mock_policy.return_value = True
        hand_delete = ServiceHandler.return_value.delete
        hand_delete.side_effect = exception.ResourceNotFound(
            name='service',
            service_id='test_id')
        obj = service.ServiceController('test_id')
        obj.delete()
        hand_delete.assert_called_with('test_id')
        self.assertEqual(404, resp_mock.status)

    def test_service_delete_ok(self, ServiceHandler, resp_mock,
                               request_mock, mock_policy):
        mock_policy.return_value = True
        hand_delete = ServiceHandler.return_value.delete
        hand_delete.return_value = None
        obj = service.ServiceController('test_id')
        obj.delete()
        hand_delete.assert_called_with('test_id')
        self.assertEqual(204, resp_mock.status)


@mock.patch('solum.common.policy.check')
@mock.patch('pecan.request', new_callable=fakes.FakePecanRequest)
@mock.patch('pecan.response', new_callable=fakes.FakePecanResponse)
@mock.patch('solum.api.handlers.service_handler.ServiceHandler')
class TestServicesController(base.BaseTestCase):
    def setUp(self):
        super(TestServicesController, self).setUp()
        objects.load()

    def test_services_get_all(self, handler_mock, resp_mock,
                              request_mock, mock_policy):
        mock_policy.return_value = True
        hand_get_all = handler_mock.return_value.get_all
        fake_service = fakes.FakeService()
        hand_get_all.return_value = [fake_service]
        obj = service.ServicesController()
        resp = obj.get_all()
        self.assertIsNotNone(resp)
        self.assertEqual(fake_service.name, resp['result'][0].name)
        self.assertEqual(fake_service.description,
                         resp['result'][0].description)
        self.assertEqual(fake_service.project_id, resp['result'][0].project_id)
        self.assertEqual(fake_service.uuid, resp['result'][0].uuid)
        hand_get_all.assert_called_with()
        self.assertEqual(200, resp_mock.status)

    def test_services_post(self, handler_mock, resp_mock,
                           request_mock, mock_policy):
        mock_policy.return_value = True
        json_create = {'name': 'foo',
                       'description': 'test_desc_service',
                       'user_id': 'user_id_test',
                       'project_id': 'project_id_test'}
        request_mock.body = json.dumps(json_create)
        request_mock.content_type = 'application/json'
        handler_create = handler_mock.return_value.create
        handler_create.return_value = fakes.FakeService()
        service.ServicesController().post()
        handler_create.assert_called_with(json_create)
        self.assertEqual(201, resp_mock.status)
        handler_create.assert_called_once_with(json_create)

    def test_services_post_nodata(self, handler_mock, resp_mock,
                                  request_mock, mock_policy):
        mock_policy.return_value = True
        request_mock.body = ''
        request_mock.content_type = 'application/json'
        handler_create = handler_mock.return_value.create
        handler_create.return_value = fakes.FakeService()
        ret_val = service.ServicesController().post()
        self.assertEqual("Missing argument: \"data\"",
                         str(ret_val['faultstring']))
        self.assertEqual(400, resp_mock.status)


class TestServiceAsDict(base.BaseTestCase):

    scenarios = [
        ('none', dict(data=None)),
        ('one', dict(data={'name': 'foo'})),
        ('full', dict(data={'uri': 'http://example.com/v1/services/x1',
                            'name': 'Example-service',
                            'type': 'service',
                            'tags': ['small'],
                            'project_id': '1dae5a09ef2b4d8cbf3594b0eb4f6b94',
                            'user_id': '55f41cf46df74320b9486a35f5d28a11',
                            'description': 'A service'}))
    ]

    def test_as_dict(self):
        objects.load()
        if self.data is None:
            s = servicemodel.Service()
            self.data = {}
        else:
            s = servicemodel.Service(**self.data)
        if 'uri' in self.data:
            del self.data['uri']
        if 'type' in self.data:
            del self.data['type']
        self.assertEqual(self.data,
                         s.as_dict(objects.registry.Service))
