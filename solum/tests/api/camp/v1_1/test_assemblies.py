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
from unittest import mock


from solum.api.controllers.camp.v1_1 import assemblies
from solum import objects
from solum.tests import base
from solum.tests import fakes


@mock.patch('pecan.request', new_callable=fakes.FakePecanRequest)
@mock.patch('pecan.response', new_callable=fakes.FakePecanResponse)
@mock.patch('solum.api.handlers.camp.assembly_handler.AssemblyHandler')
@mock.patch('solum.api.handlers.camp.plan_handler.PlanHandler')
class TestAssemblies(base.BaseTestCase):
    def setUp(self):
        super(TestAssemblies, self).setUp()
        objects.load()

    def test_assemblies_get(self, PlanHandler, AssemblyHandler, resp_mock,
                            request_mock):
        hand_get_all = AssemblyHandler.return_value.get_all
        fake_assembly = fakes.FakeAssembly()
        hand_get_all.return_value = [fake_assembly]

        resp = assemblies.AssembliesController().get()
        self.assertIsNotNone(resp)
        self.assertEqual(200, resp_mock.status)
        self.assertIsNotNone(resp['result'].assembly_links)
        assembly_links = resp['result'].assembly_links
        self.assertEqual(1, len(assembly_links))
        self.assertEqual(fake_assembly.name, assembly_links[0].target_name)

    def test_assemblies_post_no_content_type(self, PlanHandler,
                                             AssemblyHandler, resp_mock,
                                             request_mock):
        # creating an assembly requires a Content-Type so the CAMP impl
        # can figure out which mechanism the user wants
        request_mock.content_type = None

        assemblies.AssembliesController().post()
        self.assertEqual(415, resp_mock.status)

    def test_assemblies_post_ref_none(self, PlanHandler, AssemblyHandler,
                                      resp_mock, request_mock):
        # a Content-Type of 'application/json' indicates that the user is
        # providing a JSON object that references either a plan or a PDP
        request_mock.content_type = 'application/json'
        request_mock.body = None

        assemblies.AssembliesController().post()
        self.assertEqual(400, resp_mock.status)

    def test_assemblies_post_ref_empty_json(self, PlanHandler, AssemblyHandler,
                                            resp_mock, request_mock):
        # a Content-Type of 'application/json' indicates that the user is
        # providing a JSON object that references either a plan or a PDP
        request_mock.content_type = 'application/json'
        request_mock.body = '{}'

        assemblies.AssembliesController().post()
        self.assertEqual(400, resp_mock.status)

    def test_assemblies_post_ref_bad_rel_uri(self, PlanHandler,
                                             AssemblyHandler, resp_mock,
                                             request_mock):
        # a Content-Type of 'application/json' indicates that the user is
        # providing a JSON object that references either a plan or a PDP
        ref_object = {'plan_uri':
                      '../fooble/24e3974c-195d-4a6a-96b0-7924ed3c742a'}
        request_mock.content_type = 'application/json'
        request_mock.body = json.dumps(ref_object)

        assemblies.AssembliesController().post()
        self.assertEqual(400, resp_mock.status)

    def test_assemblies_post_ref_rel_uris(self, PlanHandler, AssemblyHandler,
                                          resp_mock, request_mock):
        hand_get = PlanHandler.return_value.get
        hand_get.return_value = fakes.FakePlan()

        hand_create_from_plan = AssemblyHandler.return_value.create_from_plan
        fake_assembly = fakes.FakeAssembly()
        hand_create_from_plan.return_value = fake_assembly

        cntrl = assemblies.AssembliesController()

        # test reference to CAMP plan relative to assemblies
        ref_object = {'plan_uri':
                      '../plans/24e3974c-195d-4a6a-96b0-7924ed3c742a'}
        request_mock.content_type = 'application/json'
        request_mock.body = json.dumps(ref_object)

        resp = cntrl.post()
        self.assertIsNotNone(resp)
        self.assertEqual(201, resp_mock.status)
        self.assertIsNotNone(resp_mock.location)
        self.assertEqual(fake_assembly.name, resp['name'])

        # test reference to Solum plan relative to assemblies
        ref_object = {'plan_uri':
                      '../../../v1/plans/24e3974c-195d-4a6a-96b0-7924ed3c742a'}
        request_mock.content_type = 'application/json'
        request_mock.body = json.dumps(ref_object)

        resp = cntrl.post()
        self.assertIsNotNone(resp)
        self.assertEqual(201, resp_mock.status)
        self.assertIsNotNone(resp_mock.location)
        self.assertEqual(fake_assembly.name, resp['name'])

        # test reference to CAMP plan relative to root
        ref_object = {'plan_uri':
                      '/camp/v1_1/plans/24e3974c-195d-4a6a-96b0-7924ed3c742a'}
        request_mock.content_type = 'application/json'
        request_mock.body = json.dumps(ref_object)

        resp = cntrl.post()
        self.assertIsNotNone(resp)
        self.assertEqual(201, resp_mock.status)
        self.assertIsNotNone(resp_mock.location)
        self.assertEqual(fake_assembly.name, resp['name'])

        # test reference to Solum plan relative to root
        ref_object = {'plan_uri':
                      '/v1/plans/24e3974c-195d-4a6a-96b0-7924ed3c742a'}
        request_mock.content_type = 'application/json'
        request_mock.body = json.dumps(ref_object)

        resp = cntrl.post()
        self.assertIsNotNone(resp)
        self.assertEqual(201, resp_mock.status)
        self.assertIsNotNone(resp_mock.location)
        self.assertEqual(fake_assembly.name, resp['name'])
