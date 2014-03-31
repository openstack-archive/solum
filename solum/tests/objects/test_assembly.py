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

from solum.objects import registry
from solum.objects.sqlalchemy import assembly
from solum.tests import base
from solum.tests import utils


class TestAssembly(base.BaseTestCase):
    def setUp(self):
        super(TestAssembly, self).setUp()
        self.db = self.useFixture(utils.Database())
        self.ctx = utils.dummy_context()

        self.data = [{'project_id': 'project_id_blah',
                      'uuid': 'ce43e347f0b0422825245b3e5f140a81cef6e65b',
                      'user_id': 'fred',
                      'name': 'assembly1',
                      'description': 'test assembly',
                      'trigger_id': 'trigger-uuid-1234',
                      'tags': 'assembly tags',
                      'plan_id': 'plan_id_1',
                      'status': 'Building',
                      'application_uri': 'http://192.168.78.21:5000'}]
        utils.create_models_from_data(assembly.Assembly, self.data, self.ctx)

    def test_objects_registered(self):
        self.assertTrue(registry.Assembly)
        self.assertTrue(registry.AssemblyList)

    def test_get_all(self):
        lst = assembly.AssemblyList()
        self.assertEqual(1, len(lst.get_all(self.ctx)))

    def test_check_data(self):
        ta = assembly.Assembly().get_by_id(self.ctx, self.data[0]['id'])
        for key, value in self.data[0].items():
            self.assertEqual(value, getattr(ta, key))

    def test_check_data_by_trigger_id(self):
        ta = assembly.Assembly().get_by_trigger_id(self.ctx, self.data[0][
            'trigger_id'])
        for key, value in self.data[0].items():
            self.assertEqual(value, getattr(ta, key))
