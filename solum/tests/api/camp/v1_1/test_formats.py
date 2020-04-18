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

from unittest import mock

from solum.api.controllers.camp.v1_1 import formats
from solum import objects
from solum.tests import base
from solum.tests import fakes


@mock.patch('pecan.request', new_callable=fakes.FakePecanRequest)
@mock.patch('pecan.response', new_callable=fakes.FakePecanResponse)
class TestFormats(base.BaseTestCase):
    def setUp(self):
        super(TestFormats, self).setUp()
        objects.load()

    # These tests aren't strictly "unit tests" since we don't stub-out the
    # handler for format resources. However, since that handler simply
    # looks up a static object in a static dictionary, it isn't that big
    # of a deal.

    def test_formats_get(self, resp_mock, request_mock):
        cont = formats.FormatsController()
        resp = cont.get()
        self.assertIsNotNone(resp)
        self.assertEqual(200, resp_mock.status)
        self.assertEqual('formats', resp['result'].type)
        self.assertEqual('Solum_CAMP_formats', resp['result'].name)
        format_links = resp['result'].format_links
        self.assertEqual(1, len(format_links))
        self.assertEqual('JSON', format_links[0].target_name)

    def test_get_json_format(self, resp_mock, request_mock):
        cont = formats.FormatsController()
        resp = cont.get_one('json_format')
        self.assertIsNotNone(resp)
        self.assertEqual(200, resp_mock.status)
        self.assertEqual('format', resp['result'].type)
        self.assertEqual('JSON', resp['result'].name)

    def test_format_get_not_found(self, resp_mock, request_mock):
        cont = formats.FormatsController()
        resp = cont.get_one('nonexistent_format')
        self.assertIsNotNone(resp)
        self.assertEqual(404, resp_mock.status)
