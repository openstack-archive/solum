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

from tempest import exceptions as tempest_exceptions

from functionaltests.api import base

sample_data = {"name": "test_language_pack",
               "description": "A test to create language_pack",
               "project_id": "project_id",
               "user_id": "user_id",
               "language_pack_type": "java",
               "language_implementation": "Sun",
               "compiler_versions": ["1.4", "1.5", "1.6"],
               "runtime_versions": ["1.5", "1.6", "1.7"],
               "build_tool_chain": [{
                   "type": "maven",
                   "version": "3.0"
               }, {
                   "type": "ant",
                   "version": "1.7"
               }],
               "os_platform": {"OS": "Ubuntu", "version": "12.04"},
               "attributes": {"key1": "value1", "key2": "value2"},
               "type": "language_pack"}

sample_lp = {"name": "test_language_pack",
             "git_url": "https://github.com/murali44/Solum-lp-Go.git",
             "lp_metadata": "test_metadata"}


class TestLanguagePackController(base.TestCase):

    def setUp(self):
        super(TestLanguagePackController, self).setUp()

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
        for runtime_version in data['runtime_versions']:
            self.assertIn(runtime_version, body_data['runtime_versions'])
        for build_tool in data['build_tool_chain']:
            self.assertIn(build_tool, body_data['build_tool_chain'])
        self.assertEqual(body_data['attributes'], data['attributes'])
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
        self._delete_language_pack(uuid)

    def test_language_packs_create(self):
        sample_json = json.dumps(sample_data)
        resp, body = self.client.post('v1/language_packs', sample_json)
        self.assertEqual(resp.status, 201)
        json_data = json.loads(body)
        self._assert_output_expected(json_data, sample_data)
        self._delete_language_pack(json_data['uuid'])

    def test_language_packs_create_none(self):
        self.assertRaises(tempest_exceptions.BadRequest,
                          self.client.post, 'v1/language_packs', "{}")

    def test_language_packs_get(self):
        uuid = self._create_language_pack()
        resp, body = self.client.get('v1/language_packs/%s' % uuid)
        self.assertEqual(resp.status, 200)
        json_data = json.loads(body)
        self._assert_output_expected(json_data, sample_data)
        self._delete_language_pack(uuid)

    def test_language_packs_get_not_found(self):
        self.assertRaises(tempest_exceptions.NotFound,
                          self.client.get, 'v1/language_packs/not_found')

    def test_language_packs_put(self):
        self.skipTest("Tags update not implemented yet in python-glanceclient")
        # See http://goo.gl/vg9h6G
        uuid = self._create_language_pack()
        updated_data = {"name": "test_language_pack_updated",
                        "description": "A test to create language_pack update",
                        "language_pack_type": "python",
                        "language_implementation": "py",
                        "runtime_versions": ["1.3", "1.5"],
                        "compiler_versions": ["1.4", "1.7"],
                        "build_tool_chain": [{
                            "type": "maven",
                            "version": "3.1"
                        }, {
                            "type": "gradle",
                            "version": "0.9"
                        }],
                        "os_platform": {"OS": "Fedora", "version": "17"},
                        "attributes": {"key11": "value11", "key2": "value22"},
                        "type": "language_pack"}
        updated_json = json.dumps(updated_data)
        resp, body = self.client.put('v1/language_packs/%s' % uuid,
                                     updated_json)
        self.assertEqual(resp.status, 200)
        json_data = json.loads(body)
        self._assert_output_expected(json_data, updated_data)
        self._delete_language_pack(uuid)

    def test_language_packs_put_not_found(self):
        updated_data = {"name": "test_language_pack_updated",
                        "description": "A test to create language_pack update",
                        "language_pack_type": "python",
                        "language_implementation": "py",
                        "runtime_versions": ["1.3", "1.5"],
                        "compiler_versions": ["1.4", "1.7"],
                        "build_tool_chain": [{
                            "type": "maven",
                            "version": "3.1"
                        }, {
                            "type": "gradle",
                            "version": "0.9"
                        }],
                        "os_platform": {"OS": "Fedora", "version": "17"},
                        "attributes": {"key11": "value11", "key2": "value22"},
                        "type": "language_pack"}
        updated_json = json.dumps(updated_data)
        self.assertRaises(tempest_exceptions.NotFound,
                          self.client.put, 'v1/language_packs/not_found',
                          updated_json)

    def test_language_packs_put_none(self):
        self.assertRaises(tempest_exceptions.BadRequest,
                          self.client.put, 'v1/language_packs/any', "{}")

    def test_language_packs_delete(self):
        uuid = self._create_language_pack()
        resp, body = self.client.delete('v1/language_packs/%s' % uuid)
        self.assertEqual(resp.status, 204)
        self.assertEqual(body, '')

    def test_language_packs_delete_not_found(self):
        self.assertRaises(tempest_exceptions.NotFound,
                          self.client.delete, 'v1/language_packs/not_found')

    def test_language_packs_build(self):
        sample_json = json.dumps(sample_lp)
        resp, body = self.builderclient.post('v1/images', sample_json)
        self.assertEqual(resp.status, 201)
        json_data = json.loads(body)
        self.assertEqual(json_data["state"], "PENDING")
        self.assertEqual(json_data["name"], "test_language_pack")
        self.builderclient.delete('v1/images/%s' % json_data["uuid"])
