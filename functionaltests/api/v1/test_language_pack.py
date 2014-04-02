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

import json

from functionaltests.api import base

sample_data = {"name": "test_language_pack",
               "description": "A test to create language_pack",
               "project_id": "project_id",
               "user_id": "user_id",
               "language_pack_type": "java",
               "language_implementation": "Sun",
               "compiler_versions": ["1.4", "1.5", "1.6"],
               "os_platform": {"OS": "Ubuntu", "version": "12.04"},
               "type": "language_pack"}


class TestLanguagePackController(base.TestCase):

    def setUp(self):
        super(TestLanguagePackController, self).setUp()
        self.addCleanup(self._delete_all)

    def _delete_all(self):
        resp, body = self.client.get('v1/language_packs')
        data = json.loads(body)
        self.assertEqual(resp.status, 200)
        [self._delete_language_pack(pl['uuid']) for pl in data]

    def _assert_output_expected(self, body_data, data):
        self.assertEqual(body_data['description'], data['description'])
        self.assertEqual(body_data['name'], data['name'])
        self.assertEqual(body_data['language_implementation'],
                         data['language_implementation'])
        self.assertEqual(body_data['language_pack_type'],
                         data['language_pack_type'])
        self.assertEqual(body_data['type'], 'language_pack')
        self.assertEqual(len(body_data['compiler_versions']),
                         len(data['compiler_versions']))
        for compiler_version in data['compiler_versions']:
            self.assertIn(compiler_version, body_data['compiler_versions'])
        self.assertEqual(body_data['os_platform']['OS'],
                         data['os_platform']['OS'])
        self.assertEqual(body_data['os_platform']['version'],
                         data['os_platform']['version'])
        self.assertIsNotNone(body_data['uuid'])

    def _delete_language_pack(self, uuid):
        resp, _ = self.client.delete('v1/language_packs/%s' % uuid)
        self.assertEqual(resp.status, 204)

    def _create_language_pack(self):
        jsondata = json.dumps(sample_data)
        resp, body = self.client.post('v1/language_packs', jsondata)
        self.assertEqual(resp.status, 201)
        out_data = json.loads(body)
        uuid = out_data['uuid']
        self.assertIsNotNone(uuid)
        return uuid

    def test_language_packs_get_all(self):
        uuid = self._create_language_pack()
        resp, body = self.client.get('v1/language_packs')
        data = json.loads(body)
        self.assertEqual(resp.status, 200)
        filtered = [pl for pl in data if pl['uuid'] == uuid]
        self.assertEqual(filtered[0]['uuid'], uuid)

    def test_language_packs_create(self):
        sample_json = json.dumps(sample_data)
        resp, body = self.client.post('v1/language_packs', sample_json)
        self.assertEqual(resp.status, 201)
        json_data = json.loads(body)
        self._assert_output_expected(json_data, sample_data)
        self._delete_language_pack(json_data['uuid'])

    def test_language_packs_get(self):
        uuid = self._create_language_pack()
        resp, body = self.client.get('v1/language_packs/%s' % uuid)
        self.assertEqual(resp.status, 200)
        json_data = json.loads(body)
        self._assert_output_expected(json_data, sample_data)
        self._delete_language_pack(uuid)

    def test_language_packs_put(self):
        uuid = self._create_language_pack()
        updated_data = {"name": "test_language_pack updated",
                        "description": "A test to create language_pack update",
                        "language_pack_type": "python",
                        "language_implementation": "py",
                        "compiler_versions": ["1.4", "1.7"],
                        "os_platform": {"OS": "Fedora", "version": "17"},
                        "type": "language_pack"}
        updated_json = json.dumps(updated_data)
        resp, body = self.client.put('v1/language_packs/%s' % uuid,
                                     updated_json)
        self.assertEqual(resp.status, 200)
        json_data = json.loads(body)
        self._assert_output_expected(json_data, updated_data)
        self._delete_language_pack(uuid)

    def test_language_packs_delete(self):
        uuid = self._create_language_pack()
        resp, body = self.client.delete('v1/language_packs/%s' % uuid)
        self.assertEqual(resp.status, 204)
        self.assertEqual(body, '')
