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

from functionaltests.api import base


class PlatformDiscoveryTestCase(base.TestCase):

    def test_get_root_discovers_camp_v1_1(self):
        if base.config_set_as('camp_enabled', False):
            self.skipTest('CAMP not enabled.')
        # get our platform_endpoints container
        resp, body = (self.client.
                      request_without_auth('camp/platform_endpoints',
                                           'GET'))
        self.assertEqual(200, resp.status)
        endpoints = json.loads(body)
        self.assertEqual('platform_endpoints', endpoints['type'])
        self.assertEqual('Solum_CAMP_endpoints', endpoints['name'])
        pe_links = endpoints['platform_endpoint_links']

        # there should be one element in the Link array
        self.assertEqual(1, len(pe_links))
        camp_v1_1_link = pe_links[0]
        self.assertEqual('Solum_CAMP_v1_1_endpoint',
                         camp_v1_1_link['target_name'])

        # get the URL of the platform_endpoint and strip the base URL
        rel_ep_url = camp_v1_1_link['href'][len(self.client.base_url) + 1:]

        # get our lone platform_endpoint resource
        resp, body = (self.client.
                      request_without_auth(rel_ep_url,
                                           'GET'))
        self.assertEqual(200, resp.status)
        endpoint = json.loads(body)
        self.assertEqual('platform_endpoint', endpoint['type'])
        self.assertEqual('Solum_CAMP_v1_1_endpoint', endpoint['name'])
        self.assertEqual('CAMP 1.1', endpoint['specification_version'])
        self.assertEqual('Solum CAMP 1.1', endpoint['implementation_version'])
        self.assertEqual('KEYSTONE-2.0', endpoint['auth_scheme'])
        self.assertEqual('%s/camp/v1_1/platform' % self.client.base_url,
                         endpoint['platform_uri'])
