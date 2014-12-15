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
from solum.objects.sqlalchemy import infrastructure_stack
from solum.tests import base
from solum.tests import utils


class TestInfrastructureStack(base.BaseTestCase):
    def setUp(self):
        super(TestInfrastructureStack, self).setUp()
        self.db = self.useFixture(utils.Database())
        self.ctx = utils.dummy_context()

        self.data = [{'project_id': self.ctx.tenant,
                      'user_id': 'fred',
                      'uuid': 'ceda0408-c93d-4772-abb2-18f65189d440',
                      'name': 'o1',
                      'description': 'Scale up the resource',
                      'image_id': 'fake_image_id',
                      'heat_stack_id': 'fake_heat_stack_id'}]
        utils.create_models_from_data(infrastructure_stack.InfrastructureStack,
                                      self.data,
                                      self.ctx)

    def test_objects_registered(self):
        self.assertIsNotNone(registry.InfrastructureStack)
        self.assertIsNotNone(registry.InfrastructureStackList)

    def test_get_all(self):
        lst = infrastructure_stack.InfrastructureStackList()
        self.assertEqual(1, len(lst.get_all(self.ctx)))

    def test_check_data(self):
        pl = infrastructure_stack.InfrastructureStack().get_by_id(
            self.ctx, self.data[0]['id'])
        for key, value in self.data[0].items():
            self.assertEqual(value, getattr(pl, key))
