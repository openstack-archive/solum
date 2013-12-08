# -*- coding: utf-8 -*-
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

import requests
import testtools


class VersionDiscoveryTestCase(testtools.TestCase):
    def test_get_root_discovers_v1(self):
        r = requests.get('http://127.0.0.1:9777')
        self.assertEqual(r.status_code, 200)
        body = r.json
        self.assertEqual(len(body), 1)
        v1 = body[0]
        self.assertEqual(v1['id'], 'v1.0')
        self.assertEqual(v1['status'], 'CURRENT')
        self.assertEqual(v1['link']['target_name'], 'v1')
        self.assertEqual(v1['link']['href'], 'http://127.0.0.1:9777/v1')
