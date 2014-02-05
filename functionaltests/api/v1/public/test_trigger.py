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

import requests

from functionaltests.api import base


class TestTriggerController(base.TestCase):

    def test_trigger_post(self):
        #Using requests instead of self.client to test unauthenticated request
        resp = requests.post('http://127.0.0.1:9777/v1/public/triggers/'
                             '7ad6f35961150bf83d0afdd913f8779417e538ea')
        self.assertEqual(resp.status_code, 200)
