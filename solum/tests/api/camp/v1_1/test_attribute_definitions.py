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

from solum.api.controllers.camp.v1_1 import attribute_definitions
from solum import objects
from solum.tests import base
from solum.tests import fakes


@mock.patch('pecan.request', new_callable=fakes.FakePecanRequest)
@mock.patch('pecan.response', new_callable=fakes.FakePecanResponse)
@mock.patch('solum.api.handlers.camp.attribute_definition_handler.'
            'AttributeDefinitionHandler')
class TestAttributeDefinitions(base.BaseTestCase):
    def setUp(self):
        super(TestAttributeDefinitions, self).setUp()
        objects.load()

    def test_attribute_definition_get(self,
                                      AttributeDefinitionHandler,
                                      resp_mock,
                                      request_mock):
        hand_get = AttributeDefinitionHandler.return_value.get
        fake_attribute_definition = fakes.FakeAttributeDefinition()
        hand_get.return_value = fake_attribute_definition

        cont = attribute_definitions.AttributeDefinitionsController()
        resp = cont.get_one('some_attribute')
        self.assertIsNotNone(resp)
        self.assertEqual(200, resp_mock.status)
        self.assertEqual(fake_attribute_definition.type, resp['result'].type)
        self.assertEqual(fake_attribute_definition.name, resp['result'].name)

    def test_attribute_def_get_not_found(self,
                                         AttributeDefinitionHandler,
                                         resp_mock,
                                         request_mock):
        hand_get = AttributeDefinitionHandler.return_value.get
        hand_get.return_value = None

        cont = attribute_definitions.AttributeDefinitionsController()
        resp = cont.get_one('some_attribute')
        self.assertIsNotNone(resp)
        self.assertEqual(404, resp_mock.status)
