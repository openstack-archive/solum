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

from tempest import exceptions as tempest_exceptions
import yaml

from functionaltests.api import base

sample_data = {"version": "1",
               "name": "test_plan",
               "description": "A test to create plan",
               "artifacts": [{
                   "name": "No deus",
                   "artifact_type": "heroku",
                   "content": {
                       "href": "https://example.com/git/a.git"
                   },
                   "language_pack": "auto",
               }]}


class TestPlanController(base.TestCase):
    def setUp(self):
        super(TestPlanController, self).setUp()

    def tearDown(self):
        super(TestPlanController, self).tearDown()
        self.client.delete_created_plans()

    def _assert_output_expected(self, body_data, data):
        self.assertEqual(body_data['description'], data['description'])
        self.assertEqual(body_data['name'], data['name'])
        if body_data['artifacts']:
            self.assertEqual(body_data['artifacts'][0]['content']['href'],
                             data['artifacts'][0]['content']['href'])
        self.assertIsNotNone(body_data['uuid'])

    def test_plans_get_all(self):
        create_resp = self.client.create_plan()
        self.assertEqual(create_resp.status, 201)
        resp, body = self.client.get(
            'v1/plans', headers={'content-type': 'application/x-yaml'})
        data = yaml.load(body)
        self.assertEqual(resp.status, 200)
        uuid = create_resp.uuid
        filtered = [pl for pl in data if pl['uuid'] == uuid]
        self.assertEqual(filtered[0]['uuid'], uuid)

    def test_plans_create(self):
        resp = self.client.create_plan(data=sample_data)
        self.assertEqual(resp.status, 201)
        self._assert_output_expected(resp.data, sample_data)

    def test_plans_create_empty_yaml(self):
        # NOTE(stannie): tempest rest_client raises InvalidContentType and not
        # BadRequest because yaml content-type is not supported in their
        # _error_checker method.
        self.assertRaises(tempest_exceptions.InvalidContentType,
                          self.client.post, 'v1/plans', '{}',
                          headers={'content-type': 'application/x-yaml'})

    def test_plans_create_invalid_yaml_type(self):
        # NOTE(stannie): see test_plans_create_empty_yaml note
        self.assertRaises(tempest_exceptions.InvalidContentType,
                          self.client.post, 'v1/plans', 'invalid type',
                          headers={'content-type': 'application/x-yaml'})

    def test_plans_create_invalid_yaml_syntax(self):
        # NOTE(stannie): see test_plans_create_empty_yaml note
        self.assertRaises(tempest_exceptions.InvalidContentType,
                          self.client.post, 'v1/plans', "}invalid: y'm'l3!",
                          headers={'content-type': 'application/x-yaml'})

    def test_plans_get(self):
        create_resp = self.client.create_plan(data=sample_data)
        self.assertEqual(create_resp.status, 201)
        uuid = create_resp.uuid
        resp, body = self.client.get(
            'v1/plans/%s' % uuid,
            headers={'content-type': 'application/x-yaml'})
        self.assertEqual(resp.status, 200)
        yaml_data = yaml.load(body)
        self._assert_output_expected(yaml_data, sample_data)

    def test_plans_get_not_found(self):
        # NOTE(stannie): tempest rest_client raises InvalidContentType and not
        # NotFound because yaml content-type is not supported in their
        # _error_checker method.
        self.assertRaises(tempest_exceptions.InvalidContentType,
                          self.client.get, 'v1/plans/not_found',
                          headers={'content-type': 'application/x-yaml'})

    def test_plans_put(self):
        create_resp = self.client.create_plan()
        self.assertEqual(create_resp.status, 201)
        uuid = create_resp.uuid
        updated_data = {"version": "1",
                        "name": "test_plan_updated",
                        "description": "A test to create plan updated",
                        "type": "plan",
                        "artifacts": []}
        updated_yaml = yaml.dump(updated_data)
        resp, body = self.client.put(
            'v1/plans/%s' % uuid, updated_yaml,
            headers={'content-type': 'application/x-yaml'})
        self.assertEqual(resp.status, 200)
        yaml_data = yaml.load(body)
        self._assert_output_expected(yaml_data, updated_data)

    def test_plans_put_not_found(self):
        # NOTE(stannie): see test_plans_get_not_found note
        updated_data = {"name": "test_plan updated",
                        "description": "A test to create plan updated",
                        "type": "plan",
                        "artifacts": []}
        updated_yaml = yaml.dump(updated_data)
        self.assertRaises(tempest_exceptions.InvalidContentType,
                          self.client.put, 'v1/plans/not_found', updated_yaml,
                          headers={'content-type': 'application/x-yaml'})

    def test_plans_put_empty_yaml(self):
        # NOTE(stannie): see test_plans_create_empty_yaml note
        self.assertRaises(tempest_exceptions.InvalidContentType,
                          self.client.put, 'v1/plans/any', '{}',
                          headers={'content-type': 'application/x-yaml'})

    def test_plans_put_invalid_yaml_type(self):
        # NOTE(stannie): see test_plans_create_empty_yaml note
        self.assertRaises(tempest_exceptions.InvalidContentType,
                          self.client.put, 'v1/plans/any', 'invalid type',
                          headers={'content-type': 'application/x-yaml'})

    def test_plans_put_invalid_yaml_syntax(self):
        self.assertRaises(tempest_exceptions.InvalidContentType,
                          self.client.put, 'v1/plans/any', "}invalid: y'm'l3!",
                          headers={'content-type': 'application/x-yaml'})

    def test_plans_delete(self):
        create_resp = self.client.create_plan()
        self.assertEqual(create_resp.status, 201)
        uuid = create_resp.uuid
        resp, body = self.client.delete_plan(uuid)
        self.assertEqual(resp.status, 204)
        self.assertEqual(body, '')

    def test_plans_delete_not_found(self):
        self.assertRaises(tempest_exceptions.NotFound,
                          self.client.delete, 'v1/plans/not_found')
