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

sample_data = {"name": "test_service",
               "description": "A test to create service",
               "project_id": "project_id",
               "user_id": "user_id",
               "service_type": "mysql",
               "read_only": True,
               "type": "service"}


class TestServiceController(base.TestCase):
    def setUp(self):
        super(TestServiceController, self).setUp()
        self.addCleanup(self._delete_all)

    def _delete_all(self):
        resp, body = self.client.get('v1/services')
        data = json.loads(body)
        self.assertEqual(resp.status, 200)
        [self._delete_service(ser['uuid']) for ser in data]

    def _assert_output_expected(self, body_data, data):
        self.assertEqual(body_data['description'], data['description'])
        self.assertEqual(body_data['name'], data['name'])
        self.assertEqual(body_data['service_type'], data['service_type'])
        self.assertEqual(body_data['read_only'], data['read_only'])
        self.assertEqual(body_data['type'], 'service')
        self.assertIsNotNone(body_data['uuid'])

    def _delete_service(self, uuid):
        resp, _ = self.client.delete('v1/services/%s' % uuid)
        self.assertEqual(resp.status, 204)

    def _create_service(self):
        jsondata = json.dumps(sample_data)
        resp, body = self.client.post('v1/services', jsondata)
        self.assertEqual(resp.status, 201)
        out_data = json.loads(body)
        uuid = out_data['uuid']
        self.assertIsNotNone(uuid)
        return uuid

    def test_services_get_all(self):
        uuid = self._create_service()
        resp, body = self.client.get('v1/services')
        data = json.loads(body)
        self.assertEqual(resp.status, 200)
        filtered = [ser for ser in data if ser['uuid'] == uuid]
        self.assertEqual(filtered[0]['uuid'], uuid)

    def test_services_create(self):
        sample_json = json.dumps(sample_data)
        resp, body = self.client.post('v1/services', sample_json)
        self.assertEqual(resp.status, 201)
        json_data = json.loads(body)
        self._assert_output_expected(json_data, sample_data)
        self._delete_service(json_data['uuid'])

    def test_services_create_none(self):
        self.assertRaises(tempest_exceptions.BadRequest,
                          self.client.post, 'v1/services', "{}")

    def test_services_get(self):
        uuid = self._create_service()
        resp, body = self.client.get('v1/services/%s' % uuid)
        self.assertEqual(resp.status, 200)
        json_data = json.loads(body)
        self._assert_output_expected(json_data, sample_data)
        self._delete_service(uuid)

    def test_services_get_not_found(self):
        self.assertRaises(tempest_exceptions.NotFound,
                          self.client.get, 'v1/services/not_found')

    def test_services_put(self):
        uuid = self._create_service()
        updated_data = {"name": "test_service_updated",
                        "description": "A test to create service updated",
                        "user_id": "user_id updated",
                        "service_type": "mysql updated",
                        "read_only": False}
        updated_json = json.dumps(updated_data)
        resp, body = self.client.put('v1/services/%s' % uuid, updated_json)
        self.assertEqual(resp.status, 200)
        json_data = json.loads(body)
        self._assert_output_expected(json_data, updated_data)
        self._delete_service(uuid)

    def test_services_put_not_found(self):
        updated_data = {"name": "test_service_updated",
                        "description": "A test to create service updated",
                        "user_id": "user_id updated",
                        "service_type": "mysql updated",
                        "read_only": False}
        updated_json = json.dumps(updated_data)
        self.assertRaises(tempest_exceptions.NotFound,
                          self.client.put, 'v1/services/not_found',
                          updated_json)

    def test_services_put_none(self):
        self.assertRaises(tempest_exceptions.BadRequest,
                          self.client.put, 'v1/services/any', "{}")

    def test_services_delete(self):
        uuid = self._create_service()
        resp, body = self.client.delete('v1/services/%s' % uuid)
        self.assertEqual(resp.status, 204)
        self.assertEqual(body, '')

    def test_services_delete_not_found(self):
        self.assertRaises(tempest_exceptions.NotFound,
                          self.client.delete, 'v1/services/not_found')
