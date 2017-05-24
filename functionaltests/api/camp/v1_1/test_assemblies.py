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
import yaml

from functionaltests.api import base
from functionaltests.api.camp.v1_1 import test_plans


class TestAssembliesController(base.TestCase):

    def tearDown(self):
        super(TestAssembliesController, self).tearDown()
        self.client.delete_created_assemblies()
        self.client.delete_created_plans()

    # TODO(gpilz) - this is a dup of a method in test_plans.TestPlansController
    def _create_camp_plan(self, data):
        yaml_data = yaml.dump(data)
        resp, body = self.client.post('camp/v1_1/plans', yaml_data,
                                      headers={'content-type':
                                               'application/x-yaml'})
        plan_resp = base.SolumResponse(resp=resp,
                                       body=body,
                                       body_type='json')
        uuid = plan_resp.uuid
        if uuid is not None:
            # share the Solum client's list of created plans
            self.client.created_plans.append(uuid)
        return plan_resp

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
        new_uuid = a_resp.uuid

        # try to get to the newly created assembly through the CAMP assemblies
        # resource. it would be more efficient to simply take the UUID of the
        # newly created resource and create a CAMP API URI
        # (../camp/v1_1/assemblies/<uuid>) from that, but we want to test that
        # a link to the Solum-created assembly appears in in the list of links
        # in the CAMP plans resource.
        resp, body = self.client.get('camp/v1_1/assemblies')
        self.assertEqual(200, resp.status, 'GET assemblies resource')

        # pick out the assemebly link for our new assembly uuid
        assemblies_dct = json.loads(body)
        camp_link = None
        for link in assemblies_dct['assembly_links']:
            link_uuid = link['href'].split("/")[-1]
            if link_uuid == new_uuid:
                camp_link = link

        msg = 'Unable to find link to newly created plan in CAMP plans'
        self.assertIsNotNone(camp_link, msg)

        url = camp_link['href'][len(self.client.base_url) + 1:]
        msg = ("GET Solum assembly resource for %s" %
               camp_link['target_name'])
        resp, body = self.client.get(url)
        self.assertEqual(200, resp.status, msg)

        assembly = json.loads(body)
        self.assertEqual('assembly', assembly['type'])
        self.assertEqual(base.assembly_sample_data['name'], assembly['name'])

    def test_create_camp_assembly(self):
        """Test creating a CAMP assembly from a local plan resource.

        Creates a plan resource then uses that to create an assembly resource.

        """
        if base.config_set_as('camp_enabled', False):
            self.skipTest('CAMP not enabled.')

        # create a plan using the CAMP API
        resp = self._create_camp_plan(data=test_plans.sample_data)
        self.assertEqual(201, resp.status)
        uri = (resp.data['uri']
               [len(self.client.base_url):])

        ref_obj = json.dumps({'plan_uri': uri})

        resp, body = self.client.post(
            'camp/v1_1/assemblies',
            ref_obj,
            headers={'content-type': 'application/json'})
        self.assertEqual(201, resp.status)

        assem_resp = base.SolumResponse(resp=resp,
                                        body=body,
                                        body_type='json')
        uuid = assem_resp.uuid
        if uuid is not None:
            # share the Solum client's list of created assemblies
            self.client.created_assemblies.append(uuid)

    def test_delete_plan_with_assemblies(self):
        """Test deleting a plan that has assemblies associated with it.

        Creates a plan, an assembly, then tries to delete the plan.
        """
        if base.config_set_as('camp_enabled', False):
            self.skipTest('CAMP not enabled.')

        # create a plan using the CAMP API
        resp = self._create_camp_plan(data=test_plans.sample_data)
        self.assertEqual(201, resp.status)
        plan_uri = (resp.data['uri']
                    [len(self.client.base_url):])

        ref_obj = json.dumps({'plan_uri': plan_uri})

        resp, body = self.client.post(
            'camp/v1_1/assemblies',
            ref_obj,
            headers={'content-type': 'application/json'})
        self.assertEqual(201, resp.status)

        assem_resp = base.SolumResponse(resp=resp,
                                        body=body,
                                        body_type='json')
        uuid = assem_resp.uuid
        if uuid is not None:
            # share the Solum client's list of created assemblies
            self.client.created_assemblies.append(uuid)

        # try to delete the plan before deleting the assembly
#        resp, body = self.client.delete(plan_uri[1:])
#        self.assertEqual(409, resp.status)

        self.assertRaises(tempest_exceptions.Conflict,
                          self.client.delete, plan_uri[1:])
