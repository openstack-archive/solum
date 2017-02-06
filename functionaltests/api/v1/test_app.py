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
import time

from tempest.lib import exceptions as tempest_exceptions
import yaml

from functionaltests.api import base
from functionaltests.api.common import apputils


class TestAppController(base.TestCase):

    def _assert_app_data(self, actual, expected):
        self.assertEqual(expected["name"], actual["name"])
        self.assertEqual(expected["description"], actual["description"])
        self.assertEqual(expected["languagepack"], actual["languagepack"])
        self.assertEqual(expected["trigger_actions"],
                         actual["trigger_actions"])

        self.assertEqual(expected["ports"], actual["ports"])
        self.assertEqual(expected["source"]["repository"],
                         actual["source"]["repository"])

        self.assertEqual(expected["source"]["revision"],
                         actual["source"]["revision"])

        self.assertEqual(expected["workflow_config"]["test_cmd"],
                         actual["workflow_config"]["test_cmd"])

        self.assertEqual(expected["workflow_config"]["run_cmd"],
                         actual["workflow_config"]["run_cmd"])

    def setUp(self):
        super(TestAppController, self).setUp()

    def tearDown(self):
        super(TestAppController, self).tearDown()

    def test_app_create(self):
        lp_name = self.client.create_lp()
        data = apputils.get_sample_data(languagepack=lp_name)
        resp = self.client.create_app(data=data)
        self.assertEqual(201, resp.status)
        self.client.delete_app(resp.id)
        time.sleep(2)
        self.client.delete_language_pack(lp_name)

    def test_app_create_bad_port_data(self):
        try:
            bad_data = apputils.get_sample_data()
            bad_data["ports"][0] = -1
            self.client.create_plan(data=bad_data)
        except tempest_exceptions.BadRequest:
            self.assertTrue(True)

    def test_app_create_empty_body(self):
        self.assertRaises(tempest_exceptions.BadRequest,
                          self.client.post, 'v1/apps', '{}',
                          headers={'content-type': 'application/json'})

    def test_app_patch(self):
        lp_name = self.client.create_lp()
        data = apputils.get_sample_data(languagepack=lp_name)
        create_resp = self.client.create_app(data=data)
        self.assertEqual(201, create_resp.status)

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

        self.assertEqual(200, resp.status)
        app_body = json.loads(body)
        self.assertEqual('newfakeappname', app_body["name"])
        self.assertEqual("newruncmd", app_body["workflow_config"]["run_cmd"])
        self.assertEqual("newrepo", app_body["source"]["repository"])
        self.client.delete_app(create_resp.id)
        time.sleep(2)
        self.client.delete_language_pack(lp_name)

    def test_app_get(self):
        lp_name = self.client.create_lp()
        data = apputils.get_sample_data(languagepack=lp_name)
        create_resp = self.client.create_app(data=data)
        self.assertEqual(201, create_resp.status)
        id = create_resp.id

        resp, body = self.client.get(
            'v1/apps/%s' % id,
            headers={'content-type': 'application/json'})
        self.assertEqual(200, resp.status)
        yaml_data = yaml.safe_load(body)
        self._assert_app_data(yaml_data, data)
        self.client.delete_app(create_resp.id)
        time.sleep(2)
        self.client.delete_language_pack(lp_name)

    def test_apps_get_all(self):
        lp_name = self.client.create_lp()
        data = apputils.get_sample_data(languagepack=lp_name)
        create_resp = self.client.create_app(data)
        self.assertEqual(201, create_resp.status)
        resp, body = self.client.get(
            'v1/apps', headers={'content-type': 'application/json'})
        resp_data = yaml.safe_load(body)
        self.assertEqual(200, resp.status)
        id = create_resp.id
        filtered = [app for app in resp_data if app['id'] == id]
        self.assertEqual(filtered[0]['id'], id)
        self.client.delete_app(id)
        time.sleep(2)
        self.client.delete_language_pack(lp_name)

    def test_app_delete(self):
        lp_name = self.client.create_lp()
        data = apputils.get_sample_data(languagepack=lp_name)
        create_resp = self.client.create_app(data)
        self.assertEqual(201, create_resp.status)
        id = create_resp.id
        resp, body = self.client.delete_app(id)
        self.assertEqual(202, resp.status)
        self.assertEqual('', body)
        time.sleep(2)
        self.client.delete_language_pack(lp_name)

    def test_app_delete_not_found(self):
        self.assertRaises(tempest_exceptions.NotFound,
                          self.client.delete, 'v1/apps/not_found')
