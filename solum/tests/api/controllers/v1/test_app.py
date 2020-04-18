# Copyright 2015 - Rackspace US, Inc.
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


from solum.api.controllers.v1 import app
from solum.common import exception
from solum import objects
from solum.tests import base
from solum.tests import fakes


@mock.patch('pecan.request', new_callable=fakes.FakePecanRequest)
@mock.patch('pecan.response', new_callable=fakes.FakePecanResponse)
@mock.patch('solum.api.handlers.app_handler.AppHandler')
class TestAppController(base.BaseTestCase):
    def setUp(self):
        super(TestAppController, self).setUp()
        objects.load()

    def test_app_get(self, AppHandler, resp_mock, request_mock):
        fake_app = fakes.FakeApp()
        hand_get = AppHandler.return_value.get
        hand_get.return_value = fake_app
        cont = app.AppController('test_id')
        resp = cont.get()
        self.assertIsNotNone(resp)
        hand_get.assert_called_with('test_id')
        self.assertEqual(200, resp_mock.status)

    def test_app_get_notfound(self, AppHandler, resp_mock, request_mock):
        hand_get = AppHandler.return_value.get
        hand_get.side_effect = exception.ResourceNotFound(name='app',
                                                          id='test_id')
        app.AppController('test_id').get()
        hand_get.assert_called_with('test_id')
        self.assertEqual(404, resp_mock.status)

    def test_app_patch(self, AppHandler, resp_mock, request_mock):
        json_update = {
            'name': 'newfakeappname',
            'workflow_config': {
                'run_cmd': 'newruncmd',
            },
            'source': {
                'repository': 'newrepo',
            },
        }
        request_mock.body = json.dumps(json_update)
        request_mock.content_type = 'application/json'
        request_mock.security_context = None
        hand_patch = AppHandler.return_value.patch
        fake_app = objects.registry.App(**json_update)
        hand_patch.return_value = fake_app
        app.AppController('test_id').patch()
        hand_patch.assert_called_once_with('test_id', mock.ANY)
        updated_app = hand_patch.call_args[0][1]
        self.assertEqual('newfakeappname', updated_app.name)
        self.assertEqual('newruncmd', updated_app.workflow_config['run_cmd'])
        self.assertEqual('newrepo', updated_app.source['repository'])
        self.assertEqual(200, resp_mock.status)

    def test_app_patch_no_data(self, AppHandler, resp_mock, request_mock):
        request_mock.body = ''
        request_mock.content_type = 'application/json'
        request_mock.security_context = None
        app.AppController('test_id').patch()
        self.assertEqual(400, resp_mock.status)

    def test_app_delete(self, AppHandler, resp_mock, request_mock):
        hand_delete = AppHandler.return_value.delete
        hand_delete.return_value = None
        obj = app.AppController('test_id')
        obj.delete()
        hand_delete.assert_called_with('test_id')
        self.assertEqual(202, resp_mock.status)

    def test_app_delete_notfound(self, AppHandler, resp_mock, request_mock):
        hand_delete = AppHandler.return_value.delete
        hand_delete.side_effect = exception.ResourceNotFound(
            name='missing_app', app_id='test_id')
        obj = app.AppController('test_id')
        obj.delete()
        hand_delete.assert_called_with('test_id')
        self.assertEqual(404, resp_mock.status)


@mock.patch('solum.objects.registry.Image')
@mock.patch('pecan.request', new_callable=fakes.FakePecanRequest)
@mock.patch('pecan.response', new_callable=fakes.FakePecanResponse)
@mock.patch('solum.api.handlers.app_handler.AppHandler')
class TestAppsController(base.BaseTestCase):
    def setUp(self):
        super(TestAppsController, self).setUp()
        objects.load()

    def test_apps_post(self, AppHandler, resp_mock, request_mock, mock_img):
        json_create = {'name': 'fakeapp',
                       'languagepack': 'fakelp'}
        mock_img.get_lp_by_name_or_uuid.return_value = {}
        request_mock.body = json.dumps(json_create)
        request_mock.content_type = 'application/json'
        request_mock.security_context = None
        hand_create = AppHandler.return_value.create
        fake_app = objects.registry.App(**json_create)
        hand_create.return_value = fake_app
        app.AppsController().post()
        self.assertTrue(hand_create.called)
        created_app = hand_create.call_args[0][0]
        self.assertEqual(created_app['name'], json_create['name'])
        self.assertEqual(201, resp_mock.status)

    def test_apps_post_lp_not_found(self, AppHandler, resp_mock, request_mock,
                                    mock_img):
        json_create = {'name': 'fakeapp',
                       'languagepack': 'fakelp'}
        fi = fakes.FakeImage()
        not_found = exception.ResourceNotFound(name='lp', id='fakelp')
        mock_img.get_lp_by_name_or_uuid.side_effect = not_found
        mock_img.return_value = fi
        request_mock.body = json.dumps(json_create)
        request_mock.content_type = 'application/json'
        request_mock.security_context = None
        hand_create = AppHandler.return_value.create
        fake_app = objects.registry.App(**json_create)
        hand_create.return_value = fake_app
        ret = app.AppsController().post()
        expected = 'The Languagepack fakelp could not be found.'
        self.assertEqual(expected, ret['faultstring'])

    def test_apps_post_no_data(self, AppHandler, resp_mock, request_mock,
                               mock_img):
        request_mock.body = ''
        request_mock.content_type = 'application/json'
        request_mock.security_context = None
        app.AppsController().post()
        self.assertEqual(400, resp_mock.status)

    def test_apps_post_no_app_name(self, AppHandler, resp_mock, request_mock,
                                   mock_img):
        json_create = {'name': '',
                       'languagepack': 'fakelp'}
        request_mock.body = json.dumps(json_create)
        request_mock.content_type = 'application/json'
        request_mock.security_context = None
        hand_create = AppHandler.return_value.create
        fake_app = objects.registry.App(**json_create)
        hand_create.return_value = fake_app
        app.AppsController().post()
        self.assertEqual(400, resp_mock.status)

    def test_apps_get_all(self, AppHandler, resp_mock, request_mock,
                          mock_img):
        hand_get = AppHandler.return_value.get_all
        fake_app = fakes.FakeApp()
        hand_get.return_value = [fake_app]
        resp = app.AppsController().get_all()
        self.assertIsNotNone(resp)
        self.assertEqual(200, resp_mock.status)
        hand_get.assert_called_with()
