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


class TestParameterDefinitions(base.TestCase):

    def test_assembly_parameter_definitions(self):
        """Tests normative statement RMR-03 from the CAMP v1.1 specification:

        http://docs.oasis-open.org/camp/camp-spec/v1.1/csprd02/
        camp-spec-v1.1-csprd02.pdf
        """
        if base.config_set_as('camp_enabled', False):
            self.skipTest('CAMP not enabled.')
        resp, body = self.client.get('camp/v1_1/assemblies/')
        self.assertEqual(200, resp.status, 'GET assemblies resource')
        assemblies = json.loads(body)

        # get the URL of the parameter_definitions resource
        url = (assemblies['parameter_definitions_uri']
               [len(self.client.base_url) + 1:])

        # get the parameter_definitions resource
        resp, body = self.client.get(url)
        self.assertEqual(200, resp.status,
                         'GET assembly parameter_definitions resource')
        pd_resc = json.loads(body)
        self.assertEqual('parameter_definitions', pd_resc['type'])
        self.assertIn('parameter_definition_links', pd_resc)
        pd_links = pd_resc['parameter_definition_links']

        # The assembly resource must reference parameter definitions for
        # the pdp_uri, plan_uri, pdp_file, and plan_file parameters. It
        # can reference additional parameter definitions.
        self.assertLessEqual(4,
                             len(pd_links),
                             "too few parameter definition links")
        expected_pds = ['pdp_uri', 'plan_uri', 'pdp_file', 'plan_file']
        for pd_link in pd_links:
            expected_pds.remove(pd_link['target_name'])

        self.assertEqual(0,
                         len(expected_pds),
                         ('Missing parameter_definition from %s' %
                          pd_resc['name']))

    def test_plan_parameter_definitions(self):
        """Tests normative statement RMR-06 from the CAMP v1.1 specification:

        http://docs.oasis-open.org/camp/camp-spec/v1.1/csprd02/
        camp-spec-v1.1-csprd02.pdf
        """
        if base.config_set_as('camp_enabled', False):
            self.skipTest('CAMP not enabled.')
        resp, body = self.client.get('camp/v1_1/plans/')
        self.assertEqual(200, resp.status, 'GET plans resource')
        plans = json.loads(body)

        # get the URL of the parameter_definitions resource
        url = (plans['parameter_definitions_uri']
               [len(self.client.base_url) + 1:])

        # get the parameter_definitions resource
        resp, body = self.client.get(url)
        self.assertEqual(200, resp.status,
                         'GET plans parameter_definitions resource')
        pd_resc = json.loads(body)
        self.assertEqual('parameter_definitions', pd_resc['type'])
        self.assertIn('parameter_definition_links', pd_resc)
        pd_links = pd_resc['parameter_definition_links']

        # The plan resource must reference parameter definitions for
        # the pdp_uri, plan_uri, pdp_file, and plan_file parameters. It
        # can reference additional parameter definitions.
        self.assertLessEqual(4,
                             len(pd_links),
                             "too few parameter definition links")
        expected_pds = ['pdp_uri', 'plan_uri', 'pdp_file', 'plan_file']
        for pd_link in pd_links:
            expected_pds.remove(pd_link['target_name'])

        self.assertEqual(0,
                         len(expected_pds),
                         ('Missing parameter_definition from %s' %
                          pd_resc['name']))
