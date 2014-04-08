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
import mock
import testscenarios

from solum.api.controllers.v1.datamodel import language_pack as lp_model
from solum.api.controllers.v1 import language_pack
from solum.common import exception
from solum import objects
from solum.tests import base
from solum.tests import fakes


load_tests = testscenarios.load_tests_apply_scenarios

image_sample = {"status": "active",
                "name": "nodeus",
                "tags": [
                    "solum::lp::name::fake_name",
                    "solum::lp::type::fake_type",
                    "solum::lp::compiler_version::1.3",
                    "solum::lp::compiler_version::1.4",
                    "solum::lp::compiler_version::1.5",
                    "solum::lp::runtime_version::1.4",
                    "solum::lp::runtime_version::1.5",
                    "solum::lp::runtime_version::1.6",
                    "solum::lp::implementation::Sun",
                    "solum::lp::build_tool::maven::3.0",
                    "solum::lp::build_tool::ant::2.1",
                    "solum::lp::os_platform::Ubuntu::12.04",
                    "solum::lp::attribute::attr1key::attr1value",
                    "solum::lp::attribute::attr2key::attr2value"
                ],
                "self": "/v2/images/bc68cd73",
                "id": "bc68cd73"}


@mock.patch('pecan.request', new_callable=fakes.FakePecanRequest)
@mock.patch('pecan.response', new_callable=fakes.FakePecanResponse)
@mock.patch('solum.api.handlers.language_pack_handler.LanguagePackHandler')
class TestLanguagePackController(base.BaseTestCase):
    def test_language_pack_get(self, handler_mock, resp_mock, request_mock):
        handler_get = handler_mock.return_value.get
        handler_get.return_value = image_sample
        language_pack_obj = language_pack.LanguagePackController(
            'test_id')
        result = language_pack_obj.get()
        self.assertEqual(200, resp_mock.status)
        self.assertIsNotNone(result)
        handler_get.assert_called_once_with('test_id')

    def test_lp_get_not_found(self, handler_mock, resp_mock, request_mock):
        handler_get = handler_mock.return_value.get
        handler_get.side_effect = exception.ResourceNotFound(
            name='language_pack', id='test_id')
        language_pack_obj = language_pack.LanguagePackController(
            'test_id')
        language_pack_obj.get()
        self.assertEqual(404, resp_mock.status)
        handler_get.assert_called_once_with('test_id')

    def test_language_pack_put_none(self, LanguagePackHandler, resp_mock,
                                    request_mock):
        request_mock.body = None
        request_mock.content_type = 'application/json'
        hand_put = LanguagePackHandler.return_value.put
        hand_put.return_value = fakes.FakeLanguagePack()
        ret_val = language_pack.LanguagePackController('test_id').put()
        faultstring = str(ret_val['faultstring'])
        self.assertEqual("Missing argument: \"data\"", faultstring)
        self.assertEqual(400, resp_mock.status)

    def test_language_pack_put_not_found(self, LanguagePackHandler,
                                         resp_mock, request_mock):
        json_update = {'name': 'foo'}
        request_mock.body = json.dumps(json_update)
        request_mock.content_type = 'application/json'
        hand_update = LanguagePackHandler.return_value.update
        hand_update.side_effect = exception.ResourceNotFound(
            name='language_pack', id='test_id')
        language_pack.LanguagePackController('test_id').put()
        hand_update.assert_called_with('test_id', json_update)
        self.assertEqual(404, resp_mock.status)

    def test_language_pack_put_ok(self, LanguagePackHandler, resp_mock,
                                  request_mock):
        json_update = {'name': 'foo'}
        request_mock.body = json.dumps(json_update)
        request_mock.content_type = 'application/json'
        hand_update = LanguagePackHandler.return_value.update
        hand_update.return_value = fakes.FakeLanguagePack()
        language_pack.LanguagePackController('test_id').put()
        hand_update.assert_called_with('test_id', json_update)
        self.assertEqual(200, resp_mock.status)

    def test_language_pack_delete_not_found(self, LanguagePackHandler,
                                            resp_mock, request_mock):
        hand_delete = LanguagePackHandler.return_value.delete
        hand_delete.side_effect = exception.ResourceNotFound(
            name='language_pack', language_pack_id='test_id')
        obj = language_pack.LanguagePackController('test_id')
        obj.delete()
        hand_delete.assert_called_with('test_id')
        self.assertEqual(404, resp_mock.status)

    def test_language_pack_delete_ok(self, LanguagePackHandler,
                                     resp_mock, request_mock):
        hand_delete = LanguagePackHandler.return_value.delete
        hand_delete.return_value = None
        obj = language_pack.LanguagePackController('test_id')
        obj.delete()
        hand_delete.assert_called_with('test_id')
        self.assertEqual(204, resp_mock.status)


class TestLanguagePackFromImage(base.BaseTestCase):

    def test_from_image(self):
        lp = lp_model.LanguagePack.from_image(image_sample, 'fake_host_url')
        self.assertEqual(lp.name, 'nodeus')
        self.assertEqual(lp.language_pack_type, 'fake_type')
        self.assertEqual(lp.uuid, 'bc68cd73')
        self.assertEqual(lp.compiler_versions, ['1.3', '1.4', '1.5'])
        self.assertEqual(lp.runtime_versions, ['1.4', '1.5', '1.6'])
        self.assertEqual(lp.language_implementation, 'Sun')
        self.assertEqual(len(lp.build_tool_chain), 2)
        self.assertEqual(lp.build_tool_chain[0].type, 'maven')
        self.assertEqual(lp.build_tool_chain[0].version, '3.0')
        self.assertEqual(lp.os_platform, {'OS': 'Ubuntu', 'version': '12.04'})
        self.assertIn('attr1key', lp.attributes)
        self.assertIn('attr2key', lp.attributes)
        self.assertEqual(lp.attributes['attr1key'], 'attr1value')
        self.assertEqual(lp.attributes['attr2key'], 'attr2value')


class TestLanguagePackAsDict(base.BaseTestCase):

    scenarios = [
        ('none', dict(data=None)),
        ('one', dict(data={'name': 'foo'})),
        ('full', dict(data={'uri': 'http://example.com/v1/language_packs/x1',
                            'name': 'Example language_pack',
                            'type': 'language_pack',
                            'project_id': '1dae5a09ef2b4d8cbf3594b0eb4f6b94',
                            'user_id': '55f41cf46df74320b9486a35f5d28a11'}))
    ]

    def test_as_dict(self):
        objects.load()
        if self.data is None:
            s = lp_model.LanguagePack()
            self.data = {}
        else:
            s = lp_model.LanguagePack(**self.data)
        if 'uri' in self.data:
            del self.data['uri']
        if 'type' in self.data:
            del self.data['type']

        self.assertEqual(self.data, s.as_dict(objects.registry.LanguagePack))


@mock.patch('pecan.request', new_callable=fakes.FakePecanRequest)
@mock.patch('pecan.response', new_callable=fakes.FakePecanResponse)
@mock.patch('solum.api.handlers.language_pack_handler.LanguagePackHandler')
class TestLanguagePacksController(base.BaseTestCase):
    def setUp(self):
        super(TestLanguagePacksController, self).setUp()
        objects.load()

    def test_language_packs_get_all(self, LanguagePackHandler,
                                    resp_mock, request_mock):
        hand_get = LanguagePackHandler.return_value.get_all
        hand_get.return_value = []
        resp = language_pack.LanguagePacksController().get_all()
        hand_get.assert_called_with()
        self.assertEqual(200, resp_mock.status)
        self.assertIsNotNone(resp)

    def test_language_packs_post(self, LanguagePackHandler, resp_mock,
                                 request_mock):
        json_create = {'name': 'foo'}
        request_mock.body = json.dumps(json_create)
        request_mock.content_type = 'application/json'
        hand_create = LanguagePackHandler.return_value.create
        hand_create.return_value = fakes.FakeLanguagePack()
        language_pack.LanguagePacksController().post()
        hand_create.assert_called_with(json_create)
        self.assertEqual(201, resp_mock.status)

    def test_language_packs_post_nodata(self, LanguagePackHandler, resp_mock,
                                        request_mock):
        request_mock.body = ''
        request_mock.content_type = 'application/json'
        hand_create = LanguagePackHandler.return_value.create
        hand_create.return_value = fakes.FakeLanguagePack()
        ret_val = language_pack.LanguagePacksController().post()
        faultstring = str(ret_val['faultstring'])
        self.assertEqual("Missing argument: \"data\"", faultstring)
        self.assertEqual(400, resp_mock.status)
