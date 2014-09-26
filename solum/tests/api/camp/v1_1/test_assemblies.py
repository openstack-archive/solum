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

import mock

from solum.api.controllers.camp.v1_1 import assemblies
from solum import objects
from solum.tests import base
from solum.tests import fakes


@mock.patch('pecan.request', new_callable=fakes.FakePecanRequest)
@mock.patch('pecan.response', new_callable=fakes.FakePecanResponse)
@mock.patch('solum.api.handlers.assembly_handler.AssemblyHandler')
class TestAssemblies(base.BaseTestCase):
    def setUp(self):
        super(TestAssemblies, self).setUp()
        objects.load()

    def test_assemblies_get(self, AssemblyHandler, resp_mock, request_mock):
        hand_get_all = AssemblyHandler.return_value.get_all
        fake_assembly = fakes.FakeAssembly()
        hand_get_all.return_value = [fake_assembly]

        cont = assemblies.AssembliesController()
        resp = cont.get()
        self.assertIsNotNone(resp)
        self.assertEqual(200, resp_mock.status)
        self.assertIsNotNone(resp['result'].assembly_links)
        assembly_links = resp['result'].assembly_links
        self.assertEqual(1, len(assembly_links))
        self.assertEqual(fake_assembly.name, assembly_links[0].target_name)
