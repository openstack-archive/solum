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

from solum.api.controllers.camp.v1_1 import platform
from solum import objects
from solum.tests import base
from solum.tests import fakes


@mock.patch('pecan.request', new_callable=fakes.FakePecanRequest)
@mock.patch('pecan.response', new_callable=fakes.FakePecanResponse)
class TestPlatform(base.BaseTestCase):
    def setUp(self):
        super(TestPlatform, self).setUp()
        objects.load()

    def test_platform_get(self, resp_mock, request_mock):
        cont = platform.PlatformController()
        resp = cont.get()
        self.assertIsNotNone(resp)
        self.assertEqual(200, resp_mock.status)
        self.assertEqual('platform', resp['result'].type)
        self.assertEqual('Solum_CAMP_v1_1_platform', resp['result'].name)
