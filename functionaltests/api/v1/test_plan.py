#
# Copyright 2013 - Rackspace US, Inc
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
from tempest import exceptions as tempest_exceptions

sample_data = {"name": "test_plan",
               "description": "A test to create plan",
               "project_id": "project_id",
               "user_id": "user_id",
               "type": "plan",
               "artifacts": [{
                   "name": "No_deus",
                   "artifact_type": "application.heroku",
                   "content": {
                       "href": "https://example.com/git/a.git"
                   },
                   "language_pack": "auto",
               }]}


class TestPlanController(base.TestCase):
    def setUp(self):
        super(TestPlanController, self).setUp()
        self.addCleanup(self._delete_all)

    def _delete_all(self):
        resp, body = self.client.get('v1/plans')
        data = json.loads(body)
        self.assertEqual(resp.status, 200)
        [self._delete_plan(pl['uuid']) for pl in data]

    def _assert_output_expected(self, body_data, data):
        self.assertEqual(body_data['description'], data['description'])
        self.assertEqual(body_data['name'], data['name'])
        self.assertEqual(body_data['artifacts'], data['artifacts'])
        self.assertEqual(body_data['type'], 'plan')
        self.assertIsNotNone(body_data['uuid'])

    def _delete_plan(self, uuid):
        resp, _ = self.client.delete('v1/plans/%s' % uuid)
        self.assertEqual(resp.status, 204)

    def _create_plan(self):
        jsondata = json.dumps(sample_data)
        resp, body = self.client.post('v1/plans', jsondata)
        self.assertEqual(resp.status, 201)
        out_data = json.loads(body)
        uuid = out_data['uuid']
        self.assertIsNotNone(uuid)
        return uuid

    def test_plans_get_all(self):
        uuid = self._create_plan()
        resp, body = self.client.get('v1/plans')
        data = json.loads(body)
        self.assertEqual(resp.status, 200)
        filtered = [pl for pl in data if pl['uuid'] == uuid]
        self.assertEqual(filtered[0]['uuid'], uuid)

    def test_plans_create(self):
        sample_json = json.dumps(sample_data)
        resp, body = self.client.post('v1/plans', sample_json)
        self.assertEqual(resp.status, 201)
        json_data = json.loads(body)
        self._assert_output_expected(json_data, sample_data)
        self._delete_plan(json_data['uuid'])

    def test_plans_create_none(self):
        self.assertRaises(tempest_exceptions.BadRequest,
                          self.client.post, 'v1/plans', "{}")

    def test_plans_get(self):
        uuid = self._create_plan()
        resp, body = self.client.get('v1/plans/%s' % uuid)
        self.assertEqual(resp.status, 200)
        json_data = json.loads(body)
        self._assert_output_expected(json_data, sample_data)
        self._delete_plan(uuid)

    def test_plans_get_not_found(self):
        self.assertRaises(tempest_exceptions.NotFound,
                          self.client.get, 'v1/plans/not_found')

    def test_plans_put(self):
        uuid = self._create_plan()
        updated_data = {"name": "test_plan_updated",
                        "description": "A test to create plan updated",
                        "type": "plan",
                        "artifacts": []}
        updated_json = json.dumps(updated_data)
        resp, body = self.client.put('v1/plans/%s' % uuid, updated_json)
        self.assertEqual(resp.status, 200)
        json_data = json.loads(body)
        self._assert_output_expected(json_data, updated_data)
        self._delete_plan(uuid)

    def test_plans_put_not_found(self):
        updated_data = {"name": "test_plan_updated",
                        "description": "A test to create plan updated",
                        "type": "plan",
                        "artifacts": []}
        updated_json = json.dumps(updated_data)
        self.assertRaises(tempest_exceptions.NotFound,
                          self.client.put, 'v1/plans/not_found', updated_json)

    def test_plans_put_none(self):
        self.assertRaises(tempest_exceptions.BadRequest,
                          self.client.put, 'v1/plans/any', "{}")

    def test_plans_delete(self):
        uuid = self._create_plan()
        resp, body = self.client.delete('v1/plans/%s' % uuid)
        self.assertEqual(resp.status, 204)
        self.assertEqual(body, '')

    def test_plans_delete_not_found(self):
        self.assertRaises(tempest_exceptions.NotFound,
                          self.client.delete, 'v1/plans/not_found')
