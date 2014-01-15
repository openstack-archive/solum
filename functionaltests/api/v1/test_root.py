# -*- coding: utf-8 -*-
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

from solum import version

from functionaltests.api import base


class TestRootController(base.TestCase):

    def test_index(self):
        resp, body = self.client.get('')
        self.assertEqual(resp.status, 200)
        data = json.loads(body)
        self.assertEqual(data[0]['id'], 'v1.0')
        self.assertEqual(data[0]['status'], 'CURRENT')
        self.assertEqual(data[0]['link'],
                         {'href': '%s/v1' % self.client.base_url,
                          'target_name': 'v1'})

    def test_platform(self):
        resp, body = self.client.get('v1')
        self.assertEqual(resp.status, 200)
        data = json.loads(body)
        self.assertEqual(data['uri'], '%s/v1' % self.client.base_url)
        self.assertEqual(data['type'], 'platform')
        self.assertEqual(data['name'], 'solum')
        self.assertEqual(data['description'], 'solum native implementation')
        self.assertEqual(data['implementation_version'],
                         version.version_string())
        self.assertEqual(data['assemblies_uri'],
                         '%s/v1/assemblies' % self.client.base_url)
        self.assertEqual(data['services_uri'],
                         '%s/v1/services' % self.client.base_url)
        self.assertEqual(data['components_uri'],
                         '%s/v1/components' % self.client.base_url)
        self.assertEqual(data['extensions_uri'],
                         '%s/v1/extensions' % self.client.base_url)
