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

from solum.api.controllers.v1 import language_pack
from solum.tests import base
from solum.tests import fakes


@mock.patch('pecan.request', new_callable=fakes.FakePecanRequest)
@mock.patch('pecan.response', new_callable=fakes.FakePecanResponse)
class TestLanguagePackController(base.BaseTestCase):
    def test_language_pack_get(self, resp_mock, request_mock):
        language_pack_obj = language_pack.LanguagePackController(
            'test_id')
        language_pack_obj.get()
        self.assertEqual(200, resp_mock.status)


@mock.patch('pecan.request', new_callable=fakes.FakePecanRequest)
@mock.patch('pecan.response', new_callable=fakes.FakePecanResponse)
class TestLanguagePacksController(base.BaseTestCase):
    def test_language_packs_get_all(self, resp_mock, request_mock):
        language_packs_obj = language_pack.LanguagePacksController()
        language_packs_obj.get_all()
        self.assertEqual(200, resp_mock.status)
