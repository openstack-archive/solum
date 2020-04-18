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

from unittest import mock

from solum.api.controllers.camp.v1_1 import parameter_definitions as pd
from solum import objects
from solum.tests import base
from solum.tests import fakes


@mock.patch('pecan.request', new_callable=fakes.FakePecanRequest)
@mock.patch('pecan.response', new_callable=fakes.FakePecanResponse)
class TestParameterDefinitions(base.BaseTestCase):
    def setUp(self):
        super(TestParameterDefinitions, self).setUp()
        objects.load()

    # These tests aren't strictly "unit tests" since we don't stub-out the
    # handler for parameter_definition resources. However, since that handler
    # simply looks up a static object in a static dictionary, it isn't that big
    # of a deal.

    def test_deploy_params_get(self, resp_mock, request_mock):
        cont = pd.ParameterDefinitionsController()
        resp = cont.get_one('deploy_params')
        self.assertIsNotNone(resp)
        self.assertEqual(200, resp_mock.status)
        self.assertEqual('parameter_definitions', resp['result'].type)
        self.assertEqual('Solum_CAMP_deploy_parameters', resp['result'].name)

    def test_ndt_params_get(self, resp_mock, request_mock):
        cont = pd.ParameterDefinitionsController()
        resp = cont.get_one('ndt_params')
        self.assertIsNotNone(resp)
        self.assertEqual(200, resp_mock.status)
        self.assertEqual('parameter_definitions', resp['result'].type)
        self.assertEqual('Solum_CAMP_NDT_parameters', resp['result'].name)

    def test_parameter_def_get_not_found(self, resp_mock, request_mock):
        cont = pd.ParameterDefinitionsController()
        resp = cont.get_one('does_not_exist')
        self.assertIsNotNone(resp)
        self.assertEqual(404, resp_mock.status)
