# -*- coding: utf-8 -*-
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
from solum.common import yamlutils


class TestPlansController(base.TestCase):

    def tearDown(self):
        super(TestPlansController, self).tearDown()
        self.client.delete_created_plans()

    def test_get_solum_plan(self):
        """Test the CAMP plans resource.

        Test that an plan resource created through the Solum API is
        visible via the CAMP API.
        """
        if base.config_set_as('camp_enabled', False):
            self.skipTest('CAMP not enabled.')

        # create a plan using Solum
        p_resp = self.client.create_plan()
        self.assertEqual(201, p_resp.status)

        # get the CAMP plans resource
        resp, body = self.client.get('camp/v1_1/plans')
        self.assertEqual(200, resp.status, 'GET plans resource')

        plans_dct = json.loads(body)
        plan_links = plans_dct['plan_links']
        self.assertEqual(1, len(plan_links))

        p_link = plan_links[0]
        url = p_link['href'][len(self.client.base_url) + 1:]
        msg = ("GET Solum plan resource for %s" %
               p_link['target_name'])
        resp, body = self.client.get(url,
                                     headers={'content-type':
                                              'application/x-yaml'})
        self.assertEqual(200, resp.status, msg)

        # Solum plans are rendered in YAML
        plan = yamlutils.load(body)
        self.assertEqual(base.plan_sample_data['name'], plan['name'])
        self.assertEqual(base.plan_sample_data['description'],
                         plan['description'])
