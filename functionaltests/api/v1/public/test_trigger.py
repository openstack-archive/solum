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

import requests

from functionaltests.api import base
from functionaltests.api.common import apputils


class TestTriggerController(base.TestCase):

    def test_trigger_post(self):
        lp_name = self.client.create_lp()
        data = apputils.get_sample_data(languagepack=lp_name)
        resp = self.client.create_app(data=data)
        bdy = json.loads(resp.body)
        trigger_uri = bdy['trigger_uri']
        # Using requests instead of self.client to test unauthenticated request
        status_url = 'https://api.github.com/repos/u/r/statuses/{sha}'
        body_dict = {'sender': {'url': 'https://api.github.com'},
                     'pull_request': {'head': {'sha': 'asdf'}},
                     'repository': {'statuses_url': status_url}}
        body = json.dumps(body_dict)
        resp = requests.post(trigger_uri, data=body)
        self.assertEqual(202, resp.status_code)
        self.client.delete_created_apps()
        # since app delete is an async operation, wait few seconds for app
        # delete and then delete language pack (otherwise language pack
        # cannot be deleted)
        time.sleep(2)
        self.client.delete_created_lps()

    def test_trigger_post_with_empty_body(self):
        lp_name = self.client.create_lp()
        data = apputils.get_sample_data(languagepack=lp_name)
        resp = self.client.create_app(data=data)
        bdy = json.loads(resp.body)
        trigger_uri = bdy['trigger_uri']
        # Using requests instead of self.client to test unauthenticated request
        resp = requests.post(trigger_uri)
        self.assertEqual(400, resp.status_code)
        self.client.delete_created_apps()
        # since app delete is an async operation, wait few seconds for app
        # delete and then delete language pack (otherwise language pack
        # cannot be deleted)
        time.sleep(2)
        self.client.delete_created_lps()
