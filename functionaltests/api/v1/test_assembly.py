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

from functionaltests.api import base

sample_data = {"name": "test_assembly",
               "description": "A test to create assembly",
               "project_id": "project_id",
               "user_id": "user_id",
               "status": "status",
               "application_uri": "http://localhost:5000"}

plan_sample_data = {"name": "test_plan",
                    "description": "A test to create plan",
                    "project_id": "project_id",
                    "user_id": "user_id"}


class TestAssemblyController(base.TestCase):

    def _assert_output_expected(self, body_data, data):
        self.assertEqual(body_data['description'], data['description'])
        self.assertEqual(body_data['plan_uri'], data['plan_uri'])
        self.assertEqual(body_data['name'], data['name'])
        self.assertIsNotNone(body_data['uuid'])
        self.assertEqual(body_data['status'], data['status'])
        self.assertEqual(body_data['application_uri'], data['application_uri'])

    def _delete_assembly(self, uuid, plan_uuid):
        resp, _ = self.client.delete('v1/assemblies/%s' % uuid)
        self.assertEqual(resp.status, 204)
        self._delete_plan(plan_uuid)

    def _delete_plan(self, plan_uuid):
        resp, _ = self.client.delete('v1/plans/%s' % plan_uuid)
        self.assertEqual(resp.status, 204)

    def _create_assembly(self):
        p_uuid = self._create_plan()
        sample_data['plan_uri'] = "%s/v1/plans/%s" % (self.client.base_url,
                                                      p_uuid)
        jsondata = json.dumps(sample_data)
        resp, body = self.client.post('v1/assemblies', jsondata)
        self.assertEqual(resp.status, 201)
        out_data = json.loads(body)
        uuid = out_data['uuid']
        self.assertIsNotNone(uuid)
        return uuid, p_uuid

    def _create_plan(self):
        jsondata = json.dumps(plan_sample_data)
        resp, body = self.client.post('v1/plans', jsondata)
        self.assertEqual(resp.status, 201)
        out_data = json.loads(body)
        uuid = out_data['uuid']
        self.assertIsNotNone(uuid)
        return uuid

    def test_assemblies_get_all(self):
        resp, body = self.client.get('v1/assemblies')
        data = json.loads(body)
        self.assertEqual(resp.status, 200)
        self.assertEqual(data, [])

    def test_assemblies_create(self):
        p_uuid = self._create_plan()
        sample_data['plan_uri'] = "%s/v1/plans/%s" % (self.client.base_url,
                                                      p_uuid)
        sample_json = json.dumps(sample_data)
        resp, body = self.client.post('v1/assemblies', sample_json)
        self.assertEqual(resp.status, 201)
        json_data = json.loads(body)
        self._assert_output_expected(json_data, sample_data)
        self._delete_assembly(json_data['uuid'], p_uuid)

    def test_assemblies_get(self):
        uuid, plan_uuid = self._create_assembly()
        sample_data['plan_uri'] = "%s/v1/plans/%s" % (self.client.base_url,
                                                      plan_uuid)
        resp, body = self.client.get('v1/assemblies/%s' % uuid)
        self.assertEqual(resp.status, 200)
        json_data = json.loads(body)
        self._assert_output_expected(json_data, sample_data)
        self._delete_assembly(uuid, plan_uuid)

    def test_assemblies_put(self):
        uuid, plan_uuid = self._create_assembly()
        uri = "%s/v1/plans/%s" % (self.client.base_url, plan_uuid)
        updated_data = {"name": "test_assembly updated",
                        "description": "A test to create assembly updated",
                        "plan_uri": uri,
                        "project_id": "project_id updated",
                        "user_id": "user_id updated",
                        "status": "new_status",
                        "application_uri": "new_uri"}
        updated_json = json.dumps(updated_data)
        resp, body = self.client.put('v1/assemblies/%s' % uuid, updated_json)
        self.assertEqual(resp.status, 200)
        json_data = json.loads(body)
        self._assert_output_expected(json_data, updated_data)
        self._delete_assembly(uuid, plan_uuid)

    def test_assemblies_delete(self):
        uuid, plan_uuid = self._create_assembly()
        resp, body = self.client.delete('v1/assemblies/%s' % uuid)
        self.assertEqual(resp.status, 204)
        self.assertEqual(body, '')
        self._delete_plan(plan_uuid)
