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

import copy
import json

from tempest.lib import exceptions as tempest_exceptions
import yaml

from functionaltests.api import base
from functionaltests.api.v1 import test_plan as solum_tests


sample_data = {"camp_version": "CAMP 1.1",
               "name": "camp_test_plan",
               "description": "A test to create CAMP plan",
               "artifacts": [{
                   "name": "train spotter service",
                   "artifact_type": "org.python:python",
                   "language_pack": "python1",
                   "content": {"href": "https://sporgil.com/git/spotter.git"},
                   "requirements": [{
                       "requirement_type": "org.python:runtime",
                       "fulfillment": {
                           "name": "python runtime",
                           "description": "python 2.7.x runtime",
                           "characteristics": [{
                               "characteristic_type": "org.python:version",
                               "version": "[2.7, 3,0)"
                           }]
                       }
                   }]
               }]}


class TestPlansController(base.TestCase):

    def setUp(self):
        super(TestPlansController, self).setUp()

    def tearDown(self):
        super(TestPlansController, self).tearDown()
        self.client.delete_created_plans()

    def _assert_output_expected(self, body_data, data):
        self.assertEqual(body_data['name'], data['name'])
        self.assertEqual(body_data['description'], data['description'])
        if body_data['artifacts']:
            self.assertEqual(body_data['artifacts'][0]['content']['href'],
                             data['artifacts'][0]['content']['href'])
        self.assertIsNotNone(body_data['uuid'])

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

    def test_get_solum_plan(self):
        """Test the visibility of Solum-created plans

        Test that an plan resource created through the Solum API is
        visible via the CAMP API.
        """
        if base.config_set_as('camp_enabled', False):
            self.skipTest('CAMP not enabled.')

        # create a plan using Solum
        p_resp = self.client.create_plan()
        self.assertEqual(201, p_resp.status)
        new_plan = p_resp.yaml_data
        new_uuid = new_plan['uuid']

        # try to get to the newly plan created through the CAMP plans
        # resource. it would be more efficient to simply take the UUID of the
        # newly created resource and create a CAMP API URI
        # (../camp/v1_1/plans/<uuid>) from that, but we want to test that a
        # link to the Solum-created plan appears in in the list of links in
        # the CAMP plans resource.
        resp, body = self.client.get('camp/v1_1/plans')
        self.assertEqual(200, resp.status, 'GET plans resource')

        # pick out the plan link for our new plan uuid
        plans_dct = json.loads(body)
        camp_link = None
        for link in plans_dct['plan_links']:
            link_uuid = link['href'].split("/")[-1]
            if link_uuid == new_uuid:
                camp_link = link

        msg = 'Unable to find link to newly created plan in CAMP plans'
        self.assertIsNotNone(camp_link, msg)

        url = camp_link['href'][len(self.client.base_url) + 1:]
        msg = ("GET Solum plan resource for %s" %
               camp_link['target_name'])
        resp, body = self.client.get(url)
        self.assertEqual(200, resp.status, msg)

        # CAMP plans are rendered in JSON
        plan = json.loads(body)
        self.assertEqual(base.plan_sample_data['name'], plan['name'])
        self.assertEqual(base.plan_sample_data['description'],
                         plan['description'])

    def test_create_camp_plan(self):
        """Test the visibility of CAMP-created plans

        Test that an plan resource created through the CAMP API is
        visible through the Solum API.
        """
        if base.config_set_as('camp_enabled', False):
            self.skipTest('CAMP not enabled.')

        # create a plan using the CAMP API
        resp = self._create_camp_plan(data=sample_data)
        self.assertEqual(201, resp.status)
        self._assert_output_expected(resp.data, sample_data)

        uuid = resp.data['uuid']

        # get the plan using the Solum API
        resp, body = self.client.get(
            'v1/plans/%s' % uuid,
            headers={'content-type': 'application/x-yaml'})
        self.assertEqual(200, resp.status)
        yaml_data = yaml.safe_load(body)
        self._assert_output_expected(yaml_data, sample_data)

    def test_create_camp_plan_with_private_github_repo(self):
        """Test CAMP support for private git repos

        Test that CAMP support the Solum private github case.
        """
        if base.config_set_as('camp_enabled', False):
            self.skipTest('CAMP not enabled.')

        # copy the Solum test data and add a camp_version
        camp_data = copy.copy(solum_tests.sample_data_private)
        camp_data['camp_version'] = 'CAMP 1.1'

        resp = self._create_camp_plan(data=camp_data)
        self.assertEqual(201, resp.status)
        self._assert_output_expected(resp.data, camp_data)

    def test_get_no_plan(self):
        """Try to GET a CAMP plan that doesn't exist

        Test the CAMP API's ability to respond with an HTTP 404 when doing a
        GET on a non-existent plan.
        """
        if base.config_set_as('camp_enabled', False):
            self.skipTest('CAMP not enabled.')

        self.assertRaises(tempest_exceptions.NotFound,
                          self.client.get, 'camp/v1_1/plans/no_plan')

    def test_create_bad_content_type(self):
        """Try to create a CAMP plan with a bogus Content-Type

        Test that an attempt to create a plan with an incorrect Content-Type
        header results in the proper error.
        """
        if base.config_set_as('camp_enabled', False):
            self.skipTest('CAMP not enabled.')

        yaml_data = yaml.dump(sample_data)
        self.assertRaises(tempest_exceptions.InvalidContentType,
                          self.client.post, 'camp/v1_1/plans', yaml_data,
                          headers={'content-type': 'image/jpeg'})

    def test_create_no_camp_version(self):
        """Try to create a CAMP plan from input lacking 'camp_version'

        Test that an attempt to create a plan with no 'camp_version' results
        in the proper error.
        """
        if base.config_set_as('camp_enabled', False):
            self.skipTest('CAMP not enabled.')

        no_version_data = copy.copy(sample_data)
        del no_version_data['camp_version']
        no_version_str = yaml.dump(no_version_data)

        self.assertRaises(tempest_exceptions.BadRequest,
                          self.client.post, 'camp/v1_1/plans',
                          no_version_str,
                          headers={'content-type': 'application/x-yaml'})

    def test_create_bad_camp_version(self):
        """Try to create a CAMP plan from input with incorrect 'camp_version'

        Test that an attempt to create a plan with an incorrect 'camp_version'
        results in the proper error.
        """
        if base.config_set_as('camp_enabled', False):
            self.skipTest('CAMP not enabled.')

        bad_version_data = copy.copy(sample_data)
        bad_version_data['camp_version'] = 'CAMP 8.1'
        bad_version_str = yaml.dump(bad_version_data)

        self.assertRaises(tempest_exceptions.BadRequest,
                          self.client.post, 'camp/v1_1/plans',
                          bad_version_str,
                          headers={'content-type': 'application/x-yaml'})

    def test_create_empty_yaml(self):
        """Try to create a CAMP plan from an empty YAML document

        Test that an attempt to create a plan using an empty yaml document
        results in the proper error.
        """
        if base.config_set_as('camp_enabled', False):
            self.skipTest('CAMP not enabled.')

        self.assertRaises(tempest_exceptions.BadRequest,
                          self.client.post, 'camp/v1_1/plans', '{}',
                          headers={'content-type': 'application/x-yaml'})

    def test_create_invalid_yaml(self):
        """Try to create a CAMP plan from invalid YAML

        Test that an attempt to create a plan using an invalid document
        results in the proper error.
        """
        if base.config_set_as('camp_enabled', False):
            self.skipTest('CAMP not enabled.')

        self.assertRaises(tempest_exceptions.BadRequest,
                          self.client.post, 'camp/v1_1/plans', 'invalid type',
                          headers={'content-type': 'application/x-yaml'})

    def test_create_invalid_syntax(self):
        """Try to create a CAMP plan from garbled YAML

        Test that an attempt to create a plan using yaml with an invalid syntax
        results in the proper error.
        """
        if base.config_set_as('camp_enabled', False):
            self.skipTest('CAMP not enabled.')

        self.assertRaises(tempest_exceptions.BadRequest,
                          self.client.post, 'camp/v1_1/plans',
                          "}invalid: y'm'l3!",
                          headers={'content-type': 'application/x-yaml'})

    def test_delete_solum_plan_from_camp(self):
        """Test the ability to DELETE a Solum-created plan

        Test that an plan resource created through the Solum API can
        be deleted through the CAMP API.
        """
        if base.config_set_as('camp_enabled', False):
            self.skipTest('CAMP not enabled.')

        # create a plan using Solum
        create_resp = self.client.create_plan()
        self.assertEqual(201, create_resp.status)
        uuid = create_resp.uuid

        # delete the plan using CAMP
        resp, body = self.client.delete('camp/v1_1/plans/%s' % uuid)
        self.assertEqual(204, resp.status)

        # remove the plan from the list of plans so we don't try to remove it
        # twice
        self.client.created_plans.remove(uuid)

    def test_delete_camp_plan_from_solum(self):
        """Test the ability of the Solum API to delete a CAMP-created plan

        Test that an plan resource created through the CAMP API can
        be deleted through the Solum API.
        """
        if base.config_set_as('camp_enabled', False):
            self.skipTest('CAMP not enabled.')

        # create a plan using the CAMP API
        resp = self._create_camp_plan(data=sample_data)
        self.assertEqual(201, resp.status)
        self._assert_output_expected(resp.data, sample_data)

        uuid = resp.data['uuid']

        # delete the plan using the Solum API
        resp, body = self.client.delete('v1/plans/%s' % uuid)
        self.assertEqual(202, resp.status)

        # remove the plan from the list of plans so we don't try to remove it
        # twice
        self.client.created_plans.remove(uuid)

    def test_delete_no_plan(self):
        """Try to DELTE a plan that doesn't exist

        Test the ability of CAMP to respond with an HTTP 404 when the client
        tries to DELETE a plan that doesn' exist
        """
        if base.config_set_as('camp_enabled', False):
            self.skipTest('CAMP not enabled.')

        self.assertRaises(tempest_exceptions.NotFound,
                          self.client.delete, 'camp/v1_1/plans/no_plan')

    def test_patch_plan(self):
        """PATCH a CAMP plan.

        Test the ability to modify a CAMP plan using the HTTP PATCH
        method with a JSON Patch request.
        """
        if base.config_set_as('camp_enabled', False):
            self.skipTest('CAMP not enabled.')

        # create a plan using the CAMP API
        resp = self._create_camp_plan(data=sample_data)
        self.assertEqual(201, resp.status)
        uri = (resp.data['uri']
               [len(self.client.base_url) + 1:])

        patch_data = [
            {"op": "add", "path": "/tags", "value": ["foo", "baz"]}
        ]
        patch_json = json.dumps(patch_data)

        resp, body = self.client.patch(
            uri, patch_json,
            headers={'content-type': 'application/json-patch+json'})
        self.assertEqual(200, resp.status)
        json_data = json.loads(body)
        self.assertIn('tags', json_data)
        tags = json_data['tags']
        self.assertEqual(2, len(tags))
        self.assertEqual('foo', tags[0])
        self.assertEqual('baz', tags[1])

    def test_patch_no_plan(self):
        """Try to PATCH a non-existent CAMP plan

        Test that an attempt to PATCH a plan that doesn't exist results in
        an HTTP 404 "Not Found" error
        """
        if base.config_set_as('camp_enabled', False):
            self.skipTest('CAMP not enabled.')

        # use an invalid JSON Patch document to test correct error precedence
        patch_data = [
            {"op": "add", "value": ["foo", "baz"]}
        ]
        patch_json = json.dumps(patch_data)

        # use a bad Content-Type to further test correct error precedence
        self.assertRaises(tempest_exceptions.NotFound,
                          self.client.patch, 'camp/v1_1/plans/no_plan',
                          patch_json,
                          headers={'content-type':
                                   'application/x-not-a-type'})

    def test_patch_bad_content_type(self):
        """PATCH a CAMP plan using an incorrect content-type

        Test that an attempt to patch a plan with an incorrect Content-Type
        results in the proper error.
        """
        if base.config_set_as('camp_enabled', False):
            self.skipTest('CAMP not enabled.')

        # create a plan using the CAMP API
        resp = self._create_camp_plan(data=sample_data)
        self.assertEqual(201, resp.status)
        uri = (resp.data['uri']
               [len(self.client.base_url) + 1:])

        patch_data = [
            {"op": "add", "path": "/tags", "value": ["foo", "baz"]}
        ]
        patch_json = json.dumps(patch_data)

        self.assertRaises(tempest_exceptions.InvalidContentType,
                          self.client.patch, uri, patch_json,
                          headers={'content-type': 'application/x-not-a-type'})

    def test_patch_bad_json_patch(self):
        """PATCH a CAMP plan using invalid JSON Patch document

        Test that an attempt to patch a plan with a mal-formed JSON Patch
        request (missing 'path') results in the proper error.
        """
        if base.config_set_as('camp_enabled', False):
            self.skipTest('CAMP not enabled.')

        # create a plan using the CAMP API
        resp = self._create_camp_plan(data=sample_data)
        self.assertEqual(201, resp.status)
        uri = (resp.data['uri']
               [len(self.client.base_url) + 1:])

        patch_data = [
            {"op": "add", "value": ["foo", "baz"]}
        ]
        patch_json = json.dumps(patch_data)

        self.assertRaises(tempest_exceptions.BadRequest,
                          self.client.patch, uri, patch_json,
                          headers={'content-type':
                                   'application/json-patch+json'})
