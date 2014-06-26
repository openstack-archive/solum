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

import requests
import yaml

from functionaltests.api import base

assembly_data = {'name': 'test_assembly',
                 'description': 'desc assembly'}

plan_data = {'version': '1',
             'name': 'test_plan',
             'description': 'A test to create plan'}


class TestTriggerController(base.TestCase):

    def _create_assembly(self):
        plan_uuid = self._create_plan()
        assembly_data['plan_uri'] = "%s/v1/plans/%s" % (self.client.base_url,
                                                        plan_uuid)
        data = json.dumps(assembly_data)
        resp, body = self.client.post('v1/assemblies', data)
        self.assertEqual(resp.status, 201)
        out_data = json.loads(body)
        trigger_uri = out_data['trigger_uri']
        uuid = out_data['uuid']
        self.assertIsNotNone(trigger_uri)
        self.assertIsNotNone(uuid)
        return uuid, plan_uuid, trigger_uri

    def _create_plan(self):
        data = yaml.dump(plan_data)
        resp, body = self.client.post(
            'v1/plans', data,
            headers={'content-type': 'application/x-yaml'})
        self.assertEqual(resp.status, 201)
        out_data = yaml.load(body)
        uuid = out_data['uuid']
        self.assertIsNotNone(uuid)
        return uuid

    def test_trigger_post(self):

        assembly_uuid, plan_uuid, trigger_uri = self._create_assembly()
        # Using requests instead of self.client to test unauthenticated request
        resp = requests.post(trigger_uri)
        self.assertEqual(resp.status_code, 202)

        self._delete_assembly(assembly_uuid, plan_uuid)

    def _delete_assembly(self, assembly_uuid, plan_uuid):
        resp, body = self.client.delete('v1/assemblies/%s' % assembly_uuid)
        self.assertEqual(resp.status, 204)
        self.assertTrue(self.client.assembly_delete_done(assembly_uuid))
        self._delete_plan(plan_uuid)

    def _delete_plan(self, plan_uuid):
        resp, body = self.client.delete(
            'v1/plans/%s' % plan_uuid,
            headers={'content-type': 'application/x-yaml'})
        self.assertEqual(resp.status, 204)
