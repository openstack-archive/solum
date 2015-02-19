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

from tempest_lib import exceptions as tempest_exceptions

from functionaltests.api import base

sample_lp = {"name": "language_pack_name",
             "source_uri": "https://github.com/murali44/Solum-lp-Go.git"}


class TestLanguagePackController(base.TestCase):

    def setUp(self):
        super(TestLanguagePackController, self).setUp()

    def _delete_all(self):
        resp, body = self.client.get('v1/language_packs')
        data = json.loads(body)
        self.assertEqual(resp.status, 200)
        [self._delete_language_pack(pl['uuid']) for pl in data]

    def _delete_language_pack(self, uuid):
        resp, _ = self.client.delete('v1/language_packs/%s' % uuid)
        self.assertEqual(resp.status, 204)

    def _create_language_pack(self):
        jsondata = json.dumps(sample_lp)
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
        sample_json = json.dumps(sample_lp)
        resp, body = self.client.post('v1/language_packs', sample_json)
        self.assertEqual(resp.status, 201)
        json_data = json.loads(body)
        self.assertEqual(json_data["state"], "PENDING")
        self.assertEqual(json_data["name"], sample_lp['name'])
        self._delete_language_pack(json_data["uuid"])

    def test_language_packs_create_none(self):
        self.assertRaises(tempest_exceptions.BadRequest,
                          self.client.post, 'v1/language_packs', "{}")

    def test_language_packs_get(self):
        uuid = self._create_language_pack()
        resp, body = self.client.get('v1/language_packs/%s' % uuid)
        self.assertEqual(resp.status, 200)
        json_data = json.loads(body)
        self.assertEqual(json_data['source_uri'], sample_lp['source_uri'])
        self.assertEqual(json_data['name'], sample_lp['name'])
        self._delete_language_pack(uuid)

    def test_language_packs_get_not_found(self):
        self.assertRaises(tempest_exceptions.NotFound,
                          self.client.get, 'v1/language_packs/not_found')

    def test_language_packs_delete(self):
        uuid = self._create_language_pack()
        resp, body = self.client.delete('v1/language_packs/%s' % uuid)
        self.assertEqual(resp.status, 204)
        self.assertEqual(body, '')

    def test_language_packs_delete_not_found(self):
        self.assertRaises(tempest_exceptions.NotFound,
                          self.client.delete, 'v1/language_packs/not_found')
