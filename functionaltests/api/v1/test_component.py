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

from tempest.lib import exceptions as tempest_exceptions

from functionaltests.api import base

sample_data = {'name': 'test_component',
               'description': 'desc'}

assembly_sample_data = {'name': 'test_assembly',
                        'description': 'desc assembly'}

plan_sample_data = {'version': '1',
                    'name': 'test_plan',
                    'description': 'A test to create plan'}


class TestComponentController(base.TestCase):

    def setUp(self):
        super(TestComponentController, self).setUp()

    def tearDown(self):
        super(TestComponentController, self).tearDown()
        self.client.delete_created_assemblies()
        self.client.delete_created_plans()

    def _assert_output_expected(self, body_data, data):
        self.assertEqual(body_data['name'], data['name'])
        self.assertEqual(body_data['assembly_uuid'], data['assembly_uuid'])
        self.assertIsNotNone(body_data['uuid'])
        self.assertIsNotNone(body_data['project_id'])
        self.assertIsNotNone(body_data['user_id'])

    def _delete_component(self, uuid):
        resp, body = self.client.delete('v1/components/%s' % uuid)
        self.assertEqual(204, resp.status)

    def _create_component(self):
        plan_resp = self.client.create_plan()
        self.assertEqual(201, plan_resp.status,)
        assembly_resp = self.client.create_assembly(plan_uuid=plan_resp.uuid)
        self.assertEqual(201, assembly_resp.status)
        plan_uuid = plan_resp.uuid
        assembly_uuid = assembly_resp.uuid
        sample_data['assembly_uuid'] = assembly_uuid
        data = json.dumps(sample_data)
        resp, body = self.client.post('v1/components', data)
        self.assertEqual(201, resp.status)
        out_data = json.loads(body)
        uuid = out_data['uuid']
        self.assertIsNotNone(uuid)
        return uuid, assembly_uuid, plan_uuid

    def test_components_get_all(self):
        uuid, assembly_uuid, plan_uuid = self._create_component()
        resp, body = self.client.get('v1/components')
        data = json.loads(body)
        self.assertEqual(200, resp.status)
        filtered = [com for com in data if com['uuid'] == uuid]
        self.assertEqual(1, len(filtered))
        self.assertEqual(uuid, filtered[0]['uuid'])
        self._delete_component(uuid)

    def test_components_create(self):
        plan_resp = self.client.create_plan()
        self.assertEqual(201, plan_resp.status)
        assembly_resp = self.client.create_assembly(plan_uuid=plan_resp.uuid)
        self.assertEqual(201, assembly_resp.status)
        plan_uuid = plan_resp.uuid
        assembly_uuid = assembly_resp.uuid

        sample_data['assembly_uuid'] = assembly_uuid
        sample_data['plan_uri'] = "%s/v1/plans/%s" % (self.client.base_url,
                                                      plan_uuid)
        sample_json = json.dumps(sample_data)
        resp, body = self.client.post('v1/components', sample_json)
        self.assertEqual(201, resp.status)
        json_data = json.loads(body)
        self._assert_output_expected(json_data, sample_data)
        self._delete_component(json_data['uuid'])

    def test_components_create_none(self):
        self.assertRaises(tempest_exceptions.BadRequest,
                          self.client.post, 'v1/components', "{}")

    def test_components_get(self):
        uuid, assembly_uuid, plan_uuid = self._create_component()
        sample_data['plan_uri'] = "%s/v1/plans/%s" % (self.client.base_url,
                                                      plan_uuid)
        resp, body = self.client.get('v1/components/%s' % uuid)
        self.assertEqual(200, resp.status)
        json_data = json.loads(body)
        self._assert_output_expected(json_data, sample_data)
        self._delete_component(uuid)

    def test_components_get_not_found(self):
        self.assertRaises(tempest_exceptions.NotFound,
                          self.client.get, 'v1/components/not_found')

    def test_components_put(self):
        uuid, assembly_uuid, plan_uuid = self._create_component()
        updated_data = {'name': 'test_service_updated',
                        'description': 'desc updated',
                        'plan_uri': "%s/v1/plans/%s" % (self.client.base_url,
                                                        plan_uuid),
                        'assembly_uuid': assembly_uuid}
        updated_json = json.dumps(updated_data)
        resp, body = self.client.put('v1/components/%s' % uuid, updated_json)
        self.assertEqual(200, resp.status)
        json_data = json.loads(body)
        self._assert_output_expected(json_data, updated_data)
        self._delete_component(uuid)

    def test_components_put_not_found(self):
        updated_data = {'name': 'test_service_updated',
                        'description': 'desc updated',
                        'plan_uri': "%s/v1/plans/%s" % (self.client.base_url,
                                                        'not_found'),
                        'assembly_uuid': 'not_found'}
        updated_json = json.dumps(updated_data)
        self.assertRaises(tempest_exceptions.NotFound,
                          self.client.put, 'v1/components/not_found',
                          updated_json)

    def test_components_put_none(self):
        self.assertRaises(tempest_exceptions.BadRequest,
                          self.client.put, 'v1/components/any', "{}")

    def test_components_delete(self):
        uuid, assembly_uuid, plan_uuid = self._create_component()
        resp, body = self.client.delete('v1/components/%s' % uuid)
        self.assertEqual(204, resp.status)
        self.assertEqual('', body)

    def test_components_delete_not_found(self):
        self.assertRaises(tempest_exceptions.NotFound,
                          self.client.delete, 'v1/components/not_found')
