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

from solum.api.handlers import language_pack_handler
from solum.tests import base


@mock.patch('solum.objects.registry')
class TestLanguagePackHandler(base.BaseTestCase):
    def test_language_pack_get(self, mock_registry):
        mock_registry.LanguagePack.get_by_uuid.return_value = {}
        handler = language_pack_handler.LanguagePackHandler()
        resp = handler.get('test_id')
        self.assertIsNotNone(resp)
        (mock_registry.LanguagePack.get_by_uuid.
            assert_called_once_with(None, 'test_id'))

    def test_language_pack_get_all(self, mock_registry):
        mock_registry.LanguagePackList.get_all.return_value = {}
        handler = language_pack_handler.LanguagePackHandler()
        resp = handler.get_all()
        self.assertIsNotNone(resp)
        mock_registry.LanguagePackList.get_all.assert_called_once_with(None)
