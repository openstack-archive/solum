#
# Copyright 2015 - Rackspace US, Inc
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
import yaml

from functionaltests.api import base


class TestAppController(base.TestCase):

    def _get_sample_data(self):
        data = dict()
        data["name"] = "test_app_1"
        data["description"] = "descp"
        data["languagepack"] = "python"
        data["trigger_actions"] = ["test", "build", "deploy"]
        data["ports"] = [80]

        source = {}
        source['repository'] = "https://github.com"
        source['revision'] = "master"
        data["source"] = source

        workflow = {}
        workflow["test_cmd"] = "./unit_tests.sh"
        workflow["run_cmd"] = "python app.py"
        data["workflow_config"] = workflow

        return data

    def _assert_app_data(self, actual, expected):
        self.assertEqual(actual["name"], expected["name"])
        self.assertEqual(actual["description"], expected["description"])
        self.assertEqual(actual["languagepack"], expected["languagepack"])
        self.assertEqual(actual["trigger_actions"],
                         expected["trigger_actions"])

        self.assertEqual(actual["ports"], expected["ports"])
        self.assertEqual(actual["source"]["repository"],
                         expected["source"]["repository"])

        self.assertEqual(actual["source"]["revision"],
                         expected["source"]["revision"])

        self.assertEqual(actual["workflow_config"]["test_cmd"],
                         expected["workflow_config"]["test_cmd"])

        self.assertEqual(actual["workflow_config"]["run_cmd"],
                         expected["workflow_config"]["run_cmd"])

    def setUp(self):
        super(TestAppController, self).setUp()

    def tearDown(self):
        super(TestAppController, self).tearDown()
        self.client.delete_created_apps()

    def test_app_create(self):
        data = self._get_sample_data()
        resp = self.client.create_app(data=data)
        self.assertEqual(resp.status, 201)

    def test_app_create_bad_port_data(self):
        try:
            bad_data = self._get_sample_data()
            bad_data["ports"][0] = -1
            self.client.create_plan(data=bad_data)
        except tempest_exceptions.BadRequest:
            self.assertTrue(True)

    def test_app_create_empty_body(self):
        self.assertRaises(tempest_exceptions.BadRequest,
                          self.client.post, 'v1/apps', '{}',
                          headers={'content-type': 'application/json'})

    def test_app_patch(self):
        data = self._get_sample_data()
        create_resp = self.client.create_app(data=data)
        self.assertEqual(create_resp.status, 201)

        json_update = {
            'name': 'newfakeappname',
            'workflow_config': {
                'run_cmd': 'newruncmd',
            },
            'source': {
                'repository': 'newrepo',
            },
        }

        uri = 'v1/apps/%s' % create_resp.id

        resp, body = self.client.patch(
            uri, json.dumps(json_update),
            headers={'content-type': 'application/json'})

        self.assertEqual(resp.status, 200)
        app_body = json.loads(body)
        self.assertEqual(app_body["name"], 'newfakeappname')
        self.assertEqual(app_body["workflow_config"]["run_cmd"], "newruncmd")
        self.assertEqual(app_body["source"]["repository"], "newrepo")

    def test_app_get(self):
        data = self._get_sample_data()
        create_resp = self.client.create_app(data=data)
        self.assertEqual(create_resp.status, 201)
        id = create_resp.id

        resp, body = self.client.get(
            'v1/apps/%s' % id,
            headers={'content-type': 'application/json'})
        self.assertEqual(resp.status, 200)
        yaml_data = yaml.load(body)
        self._assert_app_data(yaml_data, data)

    def test_apps_get_all(self):
        data = self._get_sample_data()
        create_resp = self.client.create_app(data)
        self.assertEqual(create_resp.status, 201)
        resp, body = self.client.get(
            'v1/apps', headers={'content-type': 'application/json'})
        resp_data = yaml.load(body)
        self.assertEqual(resp.status, 200)
        id = create_resp.id
        filtered = [app for app in resp_data if app['id'] == id]
        self.assertEqual(filtered[0]['id'], id)

    def test_app_delete(self):
        data = self._get_sample_data()
        create_resp = self.client.create_app(data)
        self.assertEqual(create_resp.status, 201)
        id = create_resp.id
        resp, body = self.client.delete_app(id)
        self.assertEqual(resp.status, 202)
        self.assertEqual(body, '')

    def test_app_delete_not_found(self):
        self.assertRaises(tempest_exceptions.NotFound,
                          self.client.delete, 'v1/apps/not_found')
