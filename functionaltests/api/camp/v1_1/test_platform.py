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


class TestPlatformAndContainers(base.TestCase):

    def _test_get_resource(self, url, rtype, name):
        resp, body = self.client.get(url)
        self.assertEqual(200, resp.status, 'GET %s resource' % rtype)
        resource = json.loads(body)
        self.assertEqual(rtype, resource['type'])
        self.assertEqual(name, resource['name'])

    def test_get_platform_and_containers(self):
        if base.config_set_as('camp_enabled', False):
            self.skipTest('CAMP not enabled.')
        # get and test our platform resource
        resp, body = self.client.get('camp/v1_1/platform/')
        self.assertEqual(200, resp.status, 'GET platform resource')
        platform = json.loads(body)
        self.assertEqual('platform', platform['type'])
        self.assertEqual('Solum_CAMP_v1_1_platform', platform['name'])
        self.assertEqual('CAMP 1.1', platform['specification_version'])
        self.assertEqual('Solum CAMP 1.1', platform['implementation_version'])

        # get and test the supported formats resource
        url = (platform['supported_formats_uri']
               [len(self.client.base_url) + 1:])
        self._test_get_resource(url, 'formats', 'Solum_CAMP_formats')

        # get and test the extensions resource
        url = (platform['extensions_uri']
               [len(self.client.base_url) + 1:])
        self._test_get_resource(url, 'extensions', 'Solum_CAMP_extensions')

        # get and test the type_definitions resource
        url = (platform['type_definitions_uri']
               [len(self.client.base_url) + 1:])
        self._test_get_resource(url,
                                'type_definitions',
                                'Solum_CAMP_type_definitions')

        # get and test the platform_endpoints resource
        url = (platform['platform_endpoints_uri']
               [len(self.client.base_url) + 1:])
        self._test_get_resource(url,
                                'platform_endpoints',
                                'Solum_CAMP_endpoints')

        # get and test the assemblies collection resource
        url = platform['assemblies_uri'][len(self.client.base_url) + 1:]
        self._test_get_resource(url, 'assemblies', 'Solum_CAMP_assemblies')

        # get and test the services collection resource
        url = platform['services_uri'][len(self.client.base_url) + 1:]
        self._test_get_resource(url, 'services', 'Solum_CAMP_services')

        # get and test the plans collection resource
        url = platform['plans_uri'][len(self.client.base_url) + 1:]
        self._test_get_resource(url, 'plans', 'Solum_CAMP_plans')
