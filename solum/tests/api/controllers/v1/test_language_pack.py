# Copyright 2014 - Rackspace
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


from solum.api.controllers.v1 import language_pack
from solum.common import exception
from solum import objects
from solum.tests import base
from solum.tests import fakes


@mock.patch('solum.common.policy.check')
@mock.patch('pecan.request', new_callable=fakes.FakePecanRequest)
@mock.patch('pecan.response', new_callable=fakes.FakePecanResponse)
@mock.patch('solum.api.handlers.language_pack_handler.LanguagePackHandler')
class TestLanguagePackController(base.BaseTestCase):
    def test_language_pack_get(self, handler_mock, resp_mock,
                               request_mock, mock_policy):
        mock_policy.return_value = True
        handler_get = handler_mock.return_value.get
        handler_get.return_value = fakes.FakeImage()
        language_pack_obj = language_pack.LanguagePackController(
            'test_id')
        result = language_pack_obj.get()
        self.assertEqual(200, resp_mock.status)
        self.assertIsNotNone(result)
        handler_get.assert_called_once_with('test_id')

    def test_lp_get_not_found(self, handler_mock, resp_mock,
                              request_mock, mock_policy):
        mock_policy.return_value = True
        handler_get = handler_mock.return_value.get
        handler_get.side_effect = exception.ResourceNotFound(
            name='language_pack', image_id='test_id')
        language_pack_obj = language_pack.LanguagePackController(
            'test_id')
        language_pack_obj.get()
        self.assertEqual(404, resp_mock.status)
        handler_get.assert_called_once_with('test_id')

    def test_language_pack_delete_not_found(self, LanguagePackHandler,
                                            resp_mock, request_mock,
                                            mock_policy):
        mock_policy.return_value = True
        hand_delete = LanguagePackHandler.return_value.delete
        hand_delete.side_effect = exception.ResourceNotFound(
            name='language_pack', language_pack_id='test_id')
        obj = language_pack.LanguagePackController('test_id')
        obj.delete()
        hand_delete.assert_called_with('test_id')
        self.assertEqual(404, resp_mock.status)

    def test_language_pack_delete_ok(self, LanguagePackHandler,
                                     resp_mock, request_mock, mock_policy):
        mock_policy.return_value = True
        hand_delete = LanguagePackHandler.return_value.delete
        hand_delete.return_value = None
        obj = language_pack.LanguagePackController('test_id')
        obj.delete()
        hand_delete.assert_called_with('test_id')
        self.assertEqual(204, resp_mock.status)


@mock.patch('solum.common.policy.check')
@mock.patch('pecan.request', new_callable=fakes.FakePecanRequest)
@mock.patch('pecan.response', new_callable=fakes.FakePecanResponse)
@mock.patch('solum.api.handlers.language_pack_handler.LanguagePackHandler')
class TestLanguagePacksController(base.BaseTestCase):
    def setUp(self):
        super(TestLanguagePacksController, self).setUp()
        objects.load()

    def test_language_packs_get_all(self, LanguagePackHandler,
                                    resp_mock, request_mock, mock_policy):
        mock_policy.return_value = True
        hand_get = LanguagePackHandler.return_value.get_all
        hand_get.return_value = []
        resp = language_pack.LanguagePacksController().get_all()
        hand_get.assert_called_with()
        self.assertEqual(200, resp_mock.status)
        self.assertIsNotNone(resp)

    def test_language_packs_post(self, LanguagePackHandler, resp_mock,
                                 request_mock, mock_policy):
        mock_policy.return_value = True
        json_create = {'name': 'foo',
                       'source_uri': 'git@github.com/sample/a.git',
                       'lp_metadata': 'some metadata', 'lp_params': {}}
        request_mock.body = json.dumps(json_create)
        request_mock.content_type = 'application/json'
        hand_create = LanguagePackHandler.return_value.create
        hand_create.return_value = fakes.FakeImage()
        language_pack.LanguagePacksController().post()
        del json_create['lp_metadata']
        del json_create['lp_params']
        hand_create.assert_called_with(json_create, 'some metadata', {})
        self.assertEqual(201, resp_mock.status)

    def test_language_packs_post_nodata(self, LanguagePackHandler, resp_mock,
                                        request_mock, mock_policy):
        mock_policy.return_value = True
        request_mock.body = ''
        request_mock.content_type = 'application/json'
        hand_create = LanguagePackHandler.return_value.create
        hand_create.return_value = fakes.FakeImage()
        ret_val = language_pack.LanguagePacksController().post()
        faultstring = str(ret_val['faultstring'])
        self.assertEqual("Missing argument: \"data\"", faultstring)
        self.assertEqual(400, resp_mock.status)

    def test_language_packs_post_badname(self, LanguagePackHandler, resp_mock,
                                         request_mock, mock_policy):
        mock_policy.return_value = True
        json_create = {'name': 'foo==',
                       'source_uri': 'git@github.com/sample/a.git',
                       'lp_metadata': 'some metadata'}
        request_mock.body = json.dumps(json_create)
        request_mock.content_type = 'application/json'
        hand_create = LanguagePackHandler.return_value.create
        hand_create.return_value = fakes.FakeImage()
        ret_val = language_pack.LanguagePacksController().post()
        faultstring = str(ret_val['faultstring'])
        error_msg = 'Names must only contain a-z,0-9,-,_'
        self.assertTrue(faultstring.endswith(error_msg))
        self.assertEqual(400, resp_mock.status)

    def test_language_packs_post_capsname(self, LanguagePackHandler, resp_mock,
                                          request_mock, mock_policy):
        mock_policy.return_value = True
        json_create = {'name': 'Foo',
                       'source_uri': 'git@github.com/sample/a.git',
                       'lp_metadata': 'some metadata'}
        request_mock.body = json.dumps(json_create)
        request_mock.content_type = 'application/json'
        hand_create = LanguagePackHandler.return_value.create
        hand_create.return_value = fakes.FakeImage()
        ret_val = language_pack.LanguagePacksController().post()
        faultstring = str(ret_val['faultstring'])
        error_msg = 'Names must only contain a-z,0-9,-,_'
        self.assertTrue(faultstring.endswith(error_msg))
        self.assertEqual(400, resp_mock.status)

    def test_language_packs_post_longname(self, LanguagePackHandler, resp_mock,
                                          request_mock, mock_policy):
        mock_policy.return_value = True
        json_create = {'name': 'a' * 101,
                       'source_uri': 'git@github.com/sample/a.git',
                       'lp_metadata': 'some metadata'}
        request_mock.body = json.dumps(json_create)
        request_mock.content_type = 'application/json'
        hand_create = LanguagePackHandler.return_value.create
        hand_create.return_value = fakes.FakeImage()
        ret_val = language_pack.LanguagePacksController().post()
        faultstring = str(ret_val['faultstring'])
        error_msg = 'Names must not be longer than 100 characters'
        self.assertTrue(faultstring.endswith(error_msg))
        self.assertEqual(400, resp_mock.status)
