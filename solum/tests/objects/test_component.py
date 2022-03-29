# Copyright 2014 - Rackspace US, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from solum.common import exception
from solum.objects import registry
from solum.objects.sqlalchemy import assembly
from solum.objects.sqlalchemy import component
from solum.tests import base
from solum.tests import utils


class TestComponent(base.BaseTestCase):
    def setUp(self):
        super(TestComponent, self).setUp()
        self.db = self.useFixture(utils.Database())
        self.ctx = utils.dummy_context()
        self.data_assembly = [
            {'project_id': self.ctx.project_id,
             'uuid': 'ce43e347f0b0422825245b3e5f140a81cef6e65b',
             'user_id': 'fred',
             'name': 'assembly1',
             'description': 'test assembly',
             'trigger_id': 'trigger-uuid-1234',
             'tags': 'assembly tags',
             'plan_id': 'plan_id_1',
             'status': 'Building',
             'application_uri': 'http://192.168.78.21:5000'}]
        utils.create_models_from_data(assembly.Assembly, self.data_assembly,
                                      self.ctx)

        self.data = [{'project_id': self.ctx.project_id,
                      'user_id': 'fred',
                      'uuid': 'ce43e347f0b0422825245b3e5f140a81cef6e65b',
                      'name': 'component_no_assembly',
                      'component_type': 'xyz',
                      'description': 'test component',
                      'parent_component_id': '87d98s',
                      'tags': 'component tags',
                      'heat_stack_id': '4c712026-dcd5-4664-90b8-0915494c1332'},
                     {'project_id': self.ctx.project_id,
                      'user_id': 'fred',
                      'uuid': '70763488-72e0-44ac-a612-e94bf5488555',
                      'name': 'component_assembly',
                      'component_type': 'xyz',
                      'description': 'test component',
                      'assembly_uuid': 'ce43e347f0b042282524'
                                       '5b3e5f140a81cef6e65b',
                      'parent_component_id': '87d98s',
                      'tags': 'component tags',
                      'heat_stack_id': '4c712026-dcd5-4664-90b8-0915494c1332'}]
        utils.create_models_from_data(component.Component, self.data, self.ctx)

    def test_objects_registered(self):
        self.assertTrue(registry.Component)
        self.assertTrue(registry.ComponentList)

    def test_get_all(self):
        lst = component.ComponentList()
        self.assertEqual(2, len(lst.get_all(self.ctx)))

    def test_check_data(self):
        ta = component.Component().get_by_id(self.ctx, self.data[0]['id'])
        for key, value in self.data[0].items():
            self.assertEqual(value, getattr(ta, key))

    def test_assembly_extra_key(self):
        ta = component.Component().get_by_id(self.ctx, self.data[1]['id'])
        self.assertEqual(ta.assembly_uuid, self.data_assembly[0]['uuid'])

    def test_assembly_extra_key_optional(self):
        ta = component.Component().get_by_id(self.ctx, self.data[0]['id'])
        self.assertIsNone(ta.assembly_uuid)

    def test_assembly_extra_key_not_found(self):
        self.assertRaises(exception.ResourceNotFound, setattr,
                          component.Component(), 'assembly_uuid', '42d')
