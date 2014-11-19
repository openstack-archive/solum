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


class TestAssembliesController(base.TestCase):

    def tearDown(self):
        super(TestAssembliesController, self).tearDown()
        self.client.delete_created_assemblies()
        self.client.delete_created_plans()

    def test_get_solum_assembly(self):
        """Test the CAMP assemblies collection resource.

        Test that an assembly resource created through the Solum API is
        visible via the CAMP API.
        """
        if base.config_set_as('camp_enabled', False):
            self.skipTest('CAMP not enabled.')

        # create an assembly using Solum
        p_resp = self.client.create_plan()
        self.assertEqual(201, p_resp.status)
        a_resp = self.client.create_assembly(plan_uuid=p_resp.uuid)
        self.assertEqual(201, a_resp.status)

        # get the CAMP assemblies resource
        resp, body = self.client.get('camp/v1_1/assemblies')
        self.assertEqual(200, resp.status, 'GET assemblies resource')

        assemblies_dct = json.loads(body)
        assem_links = assemblies_dct['assembly_links']
        self.assertEqual(1, len(assem_links))

        a_link = assem_links[0]

        url = a_link['href'][len(self.client.base_url) + 1:]
        msg = ("GET Solum assembly resource for %s" %
               a_link['target_name'])
        resp, body = self.client.get(url)
        self.assertEqual(200, resp.status, msg)

        # right now, this looks like a Solum assembly, not a CAMP
        assembly = json.loads(body)
        self.assertEqual('assembly', assembly['type'])
        self.assertEqual(base.assembly_sample_data['name'], assembly['name'])
