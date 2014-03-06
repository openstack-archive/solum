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

import mock
import testscenarios

from solum.api.controllers.v1 import language_pack
from solum.common import exception
from solum.tests import base
from solum.tests import fakes


load_tests = testscenarios.load_tests_apply_scenarios


@mock.patch('pecan.request', new_callable=fakes.FakePecanRequest)
@mock.patch('pecan.response', new_callable=fakes.FakePecanResponse)
@mock.patch('solum.api.handlers.language_pack_handler.LanguagePackHandler')
class TestLanguagePackController(base.BaseTestCase):
    def test_language_pack_get(self, handler_mock, resp_mock, request_mock):
        handler_get = handler_mock.return_value.get
        handler_get.return_value = fakes.FakeLanguagePack()
        language_pack_obj = language_pack.LanguagePackController(
            'test_id')
        result = language_pack_obj.get()
        self.assertEqual(200, resp_mock.status)
        self.assertIsNotNone(result)
        handler_get.assert_called_once_with('test_id')

    def test_lp_get_not_found(self, handler_mock, resp_mock, request_mock):
        handler_get = handler_mock.return_value.get
        handler_get.side_effect = exception.NotFound(name='language_pack',
                                                     id='test_id')
        language_pack_obj = language_pack.LanguagePackController(
            'test_id')
        language_pack_obj.get()
        self.assertEqual(404, resp_mock.status)
        handler_get.assert_called_once_with('test_id')


@mock.patch('pecan.request', new_callable=fakes.FakePecanRequest)
@mock.patch('pecan.response', new_callable=fakes.FakePecanResponse)
@mock.patch('solum.api.handlers.language_pack_handler.LanguagePackHandler')
class TestLanguagePacksController(base.BaseTestCase):
    def test_language_packs_get_all(self, handler_mock, resp_mock,
                                    request_mock):
        language_packs_obj = language_pack.LanguagePacksController()
        response = language_packs_obj.get_all()
        self.assertIsNotNone(response)
        self.assertEqual(200, resp_mock.status)
