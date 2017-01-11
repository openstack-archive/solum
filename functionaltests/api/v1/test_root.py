#
# Copyright 2013 - Noorul Islam K M
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

from functionaltests.api import base
from solum import version


class TestRootController(base.TestCase):

    def test_index(self):
        resp, body = self.client.request_without_auth('', 'GET')
        self.assertEqual(200, resp.status)
        data = json.loads(body)
        self.assertEqual(data[0]['id'], 'v1.0')
        self.assertEqual(data[0]['status'], 'CURRENT')
        self.assertEqual(data[0]['link'],
                         {'href': '%s/v1' % self.client.base_url,
                          'target_name': 'v1'})

    def test_platform(self):
        resp, body = self.client.request_without_auth('v1', 'GET')
        self.assertEqual(200, resp.status)
        data = json.loads(body)
        self.assertEqual(data['uri'], '%s/v1' % self.client.base_url)
        self.assertEqual(data['type'], 'platform')
        self.assertEqual(data['name'], 'solum')
        self.assertEqual(data['description'], 'solum native implementation')
        self.assertEqual(data['implementation_version'],
                         version.version_string())
        self.assertEqual(data['plans_uri'],
                         '%s/v1/plans' % self.client.base_url)
        self.assertEqual(data['assemblies_uri'],
                         '%s/v1/assemblies' % self.client.base_url)
        self.assertEqual(data['services_uri'],
                         '%s/v1/services' % self.client.base_url)
        self.assertEqual(data['components_uri'],
                         '%s/v1/components' % self.client.base_url)
        self.assertEqual(data['extensions_uri'],
                         '%s/v1/extensions' % self.client.base_url)
        self.assertEqual(data['operations_uri'],
                         '%s/v1/operations' % self.client.base_url)
        self.assertEqual(data['sensors_uri'],
                         '%s/v1/sensors' % self.client.base_url)
        self.assertEqual(data['language_packs_uri'],
                         '%s/v1/language_packs' % self.client.base_url)
        self.assertEqual(data['pipelines_uri'],
                         '%s/v1/pipelines' % self.client.base_url)
        self.assertEqual(data['triggers_uri'],
                         '%s/v1/triggers' % self.client.base_url)
        self.assertEqual(data['infrastructure_uri'],
                         '%s/v1/infrastructure' % self.client.base_url)

    def test_request_without_auth(self):
        resp, body = self.client.request_without_auth('v1', 'GET')
        self.assertEqual(200, resp.status)
        resp, body = self.client.get('v1')
        self.assertEqual(200, resp.status)
        resp, body = self.client.request_without_auth(
            'v1/plans', 'GET', headers={'content-type': 'application/x-yaml'})
        self.assertEqual(401, resp.status)
        resp, body = self.client.get(
            'v1/plans', headers={'content-type': 'application/x-yaml'})
        self.assertEqual(200, resp.status)
