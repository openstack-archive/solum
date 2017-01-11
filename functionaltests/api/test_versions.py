#
# Copyright 2013 - Red Hat, Inc.
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


class VersionDiscoveryTestCase(base.TestCase):
    def test_get_root_discovers_v1(self):
        resp, body = self.client.get('/')
        body = json.loads(body)
        self.assertEqual(200, resp.status)
        self.assertEqual(1, len(body))
        v1 = body[0]
        self.assertEqual('v1.0', v1['id'])
        self.assertEqual('CURRENT', v1['status'])
        self.assertEqual('v1', v1['link']['target_name'])
        self.assertEqual('%s/v1' % self.client.base_url, v1['link']['href'])

    def test_delete_root_discovers_v1(self):
        resp, body = self.client.delete('/')
        body = json.loads(body)
        self.assertEqual(200, resp.status)
        self.assertEqual(1, len(body))
        v1 = body[0]
        self.assertEqual('v1.0', v1['id'])
        self.assertEqual('CURRENT', v1['status'])
        self.assertEqual('v1', v1['link']['target_name'])
        self.assertEqual('%s/v1' % self.client.base_url, v1['link']['href'])

    def test_post_root_discovers_v1(self):
        resp, body = self.client.post('/', '{}')
        body = json.loads(body)
        self.assertEqual(200, resp.status)
        self.assertEqual(1, len(body))
        v1 = body[0]
        self.assertEqual('v1.0', v1['id'])
        self.assertEqual('CURRENT', v1['status'])
        self.assertEqual('v1', v1['link']['target_name'])
        self.assertEqual('%s/v1' % self.client.base_url, v1['link']['href'])

    def test_put_root_discovers_v1(self):
        resp, body = self.client.put('/', '{}')
        body = json.loads(body)
        self.assertEqual(200, resp.status)
        self.assertEqual(1, len(body))
        v1 = body[0]
        self.assertEqual('v1.0', v1['id'])
        self.assertEqual('CURRENT', v1['status'])
        self.assertEqual('v1', v1['link']['target_name'])
        self.assertEqual('%s/v1' % self.client.base_url, v1['link']['href'])

    def test_post_no_body_root_discovers_v1(self):
        self.skipTest("POST without body will hang request: #1367470")
        resp, body = self.client.post('/', None)
        body = json.loads(body)
        self.assertEqual(200, resp.status)
        self.assertEqual(1, len(body))
        v1 = body[0]
        self.assertEqual('v1.0', v1['id'])
        self.assertEqual('CURRENT', v1['status'])
        self.assertEqual('v1', v1['link']['target_name'])
        self.assertEqual('%s/v1' % self.client.base_url, v1['link']['href'])

    def test_put_no_body_root_discovers_v1(self):
        self.skipTest("PUT without body will hang request: #1367470")
        resp, body = self.client.put('/', None)
        body = json.loads(body)
        self.assertEqual(200, resp.status)
        self.assertEqual(1, len(body))
        v1 = body[0]
        self.assertEqual('v1.0', v1['id'])
        self.assertEqual('CURRENT', v1['status'])
        self.assertEqual('v1', v1['link']['target_name'])
        self.assertEqual('%s/v1' % self.client.base_url, v1['link']['href'])
