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

from tempest import exceptions as tempest_exceptions
import yaml

from functionaltests.api import base

sample_data = {'name': 'test_service',
               'description': 'desc'}

assembly_sample_data = {'name': 'test_assembly',
                        'description': 'desc assembly'}

plan_sample_data = {'version': '1',
                    'name': 'test_plan',
                    'description': 'A test to create plan'}


class TestComponentController(base.TestCase):

    def _assert_output_expected(self, body_data, data):
        self.assertEqual(body_data['name'], data['name'])
        self.assertEqual(body_data['assembly_uuid'], data['assembly_uuid'])
        self.assertIsNotNone(body_data['uuid'])
        self.assertIsNotNone(body_data['project_id'])
        self.assertIsNotNone(body_data['user_id'])

    def _delete_component(self, uuid, assembly_uuid, plan_uuid):
        resp, body = self.client.delete('v1/components/%s' % uuid)
        self.assertEqual(resp.status, 204)
        self._delete_assembly(assembly_uuid, plan_uuid)

    def _delete_assembly(self, assembly_uuid, plan_uuid):
        resp, body = self.client.delete('v1/assemblies/%s' % assembly_uuid)
        self.assertEqual(resp.status, 204)
        if self.client.assembly_delete_done(assembly_uuid):
            self._delete_plan(plan_uuid)
        else:
            self.fail("Assembly couldn't be deleted.")

    def _delete_plan(self, plan_uuid):
        resp, body = self.client.delete(
            'v1/plans/%s' % plan_uuid,
            headers={'content-type': 'application/x-yaml'})
        self.assertEqual(resp.status, 204)

    def _create_component(self):
        assembly_uuid, plan_uuid = self._create_assembly()
        sample_data['assembly_uuid'] = assembly_uuid
        data = json.dumps(sample_data)
        resp, body = self.client.post('v1/components', data)
        self.assertEqual(resp.status, 201)
        out_data = json.loads(body)
        uuid = out_data['uuid']
        self.assertIsNotNone(uuid)
        return uuid, assembly_uuid, plan_uuid

    def _create_assembly(self):
        plan_uuid = self._create_plan()
        sample_data['plan_uri'] = "%s/v1/plans/%s" % (self.client.base_url,
                                                      plan_uuid)
        data = json.dumps(sample_data)
        resp, body = self.client.post('v1/assemblies', data)
        self.assertEqual(resp.status, 201)
        out_data = json.loads(body)
        uuid = out_data['uuid']
        self.assertIsNotNone(uuid)
        return uuid, plan_uuid

    def _create_plan(self):
        data = yaml.dump(plan_sample_data)
        resp, body = self.client.post(
            'v1/plans', data,
            headers={'content-type': 'application/x-yaml'})
        self.assertEqual(resp.status, 201)
        out_data = yaml.load(body)
        uuid = out_data['uuid']
        self.assertIsNotNone(uuid)
        return uuid

    def test_components_get_all(self):
        resp, body = self.client.get('v1/components')
        data = json.loads(body)
        self.assertEqual(resp.status, 200)
        self.assertEqual(data, [])

    def test_components_create(self):
        assembly_uuid, plan_uuid = self._create_assembly()
        sample_data['assembly_uuid'] = assembly_uuid
        sample_data['plan_uri'] = "%s/v1/plans/%s" % (self.client.base_url,
                                                      plan_uuid)
        sample_json = json.dumps(sample_data)
        resp, body = self.client.post('v1/components', sample_json)
        self.assertEqual(resp.status, 201)
        json_data = json.loads(body)
        self._assert_output_expected(json_data, sample_data)
        self._delete_component(json_data['uuid'], assembly_uuid, plan_uuid)

    def test_components_create_none(self):
        self.assertRaises(tempest_exceptions.BadRequest,
                          self.client.post, 'v1/components', "{}")

    def test_components_get(self):
        uuid, assembly_uuid, plan_uuid = self._create_component()
        sample_data['plan_uri'] = "%s/v1/plans/%s" % (self.client.base_url,
                                                      plan_uuid)
        resp, body = self.client.get('v1/components/%s' % uuid)
        self.assertEqual(resp.status, 200)
        json_data = json.loads(body)
        self._assert_output_expected(json_data, sample_data)
        self._delete_component(uuid, assembly_uuid, plan_uuid)

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
        self.assertEqual(resp.status, 200)
        json_data = json.loads(body)
        self._assert_output_expected(json_data, updated_data)
        self._delete_component(uuid, assembly_uuid, plan_uuid)

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
        self.assertEqual(resp.status, 204)
        self.assertEqual(body, '')
        self._delete_assembly(assembly_uuid, plan_uuid)

    def test_components_delete_not_found(self):
        self.assertRaises(tempest_exceptions.NotFound,
                          self.client.delete, 'v1/components/not_found')
