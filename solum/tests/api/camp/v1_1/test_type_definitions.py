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

from solum.api.controllers.camp.v1_1.datamodel import attribute_definitions
from solum.api.controllers.camp.v1_1.datamodel import type_definitions as model
from solum.api.controllers.camp.v1_1 import type_definitions
from solum import objects
from solum.tests import base
from solum.tests import fakes

TEST_ATTR_DEFINITION = (
    attribute_definitions.AttributeDefinition(type='attribute_definition',
                                              name='fake_attribute')
)

TEST_ATTR_DEF_LINK = (
    model.AttributeLink(href='fake_attribute_definition_url',
                        target_name='fake_attribute'))

TEST_TYPE_DEFINITION = (
    model.TypeDefinition(type='type_definition',
                         name='fake_type',
                         description='fake CAMP type definition',
                         attribute_definition_links=[TEST_ATTR_DEF_LINK])
)


@mock.patch('pecan.request', new_callable=fakes.FakePecanRequest)
@mock.patch('pecan.response', new_callable=fakes.FakePecanResponse)
@mock.patch('solum.api.handlers.camp.type_definition_handler.'
            'TypeDefinitionHandler')
@mock.patch('solum.api.handlers.camp.attribute_definition_handler.'
            'AttributeDefinitionHandler')
class TestTypeDefinitions(base.BaseTestCase):
    def setUp(self):
        super(TestTypeDefinitions, self).setUp()
        objects.load()

    def test_type_definitions_get(self,
                                  AttributeDefinitionHandler,
                                  TypeDefinitionHandler,
                                  resp_mock,
                                  request_mock):
        thand_get_all = TypeDefinitionHandler.return_value.get_all
        thand_get_all.return_value = [TEST_TYPE_DEFINITION]

        cont = type_definitions.TypeDefinitionsController()
        resp = cont.get()
        self.assertIsNotNone(resp)
        self.assertEqual(200, resp_mock.status)
        self.assertIsNotNone(resp['result'].type_definition_links)
        td_links = resp['result'].type_definition_links
        self.assertEqual(1, len(td_links))
        self.assertEqual(TEST_TYPE_DEFINITION.name, td_links[0].target_name)

    def test_type_definitions_get_one(self,
                                      AttributeDefinitionHandler,
                                      TypeDefinitionHandler,
                                      resp_mock,
                                      request_mock):
        ahand_get = AttributeDefinitionHandler.return_value.get
        ahand_get.return_value = TEST_ATTR_DEFINITION
        thand_get = TypeDefinitionHandler.return_value.get
        thand_get.return_value = TEST_TYPE_DEFINITION

        cont = type_definitions.TypeDefinitionsController()
        resp = cont.get_one('fake_type')
        self.assertIsNotNone(resp)
        self.assertEqual(200, resp_mock.status)
        self.assertEqual(TEST_TYPE_DEFINITION.type, resp['result'].type)
        self.assertEqual(TEST_TYPE_DEFINITION.name, resp['result'].name)
        ad_links = resp['result'].attribute_definition_links
        self.assertEqual(1, len(ad_links))
        self.assertEqual(TEST_ATTR_DEFINITION.name,
                         ad_links[0].target_name)

    def test_type_definition_get_not_found(self,
                                           AttributeDefinitionHandler,
                                           TypeDefinitionHandler,
                                           resp_mock,
                                           request_mock):
        thand_get = TypeDefinitionHandler.return_value.get
        thand_get.return_value = None

        cont = type_definitions.TypeDefinitionsController()
        resp = cont.get_one('non_existent_type')
        self.assertIsNotNone(resp)
        self.assertEqual(404, resp_mock.status)
