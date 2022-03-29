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
from solum.objects.sqlalchemy import plan
from solum.tests import base
from solum.tests import utils


class TestPlan(base.BaseTestCase):
    def setUp(self):
        super(TestPlan, self).setUp()
        self.db = self.useFixture(utils.Database())
        self.ctx = utils.dummy_context()
        raw_content = {'artifacts': [
            {'content':
             {'href': 'http://github.com/some/project'}}]}
        self.data = [{'uuid': 'test-uuid-123',
                      'name': 'fakeplan',
                      'project_id': self.ctx.project_id,
                      'user_id': 'fred',
                      'description': 'some description',
                      'raw_content': raw_content}]
        utils.create_models_from_data(plan.Plan, self.data, self.ctx)

    def test_objects_registered(self):
        self.assertTrue(registry.Plan)
        self.assertTrue(registry.PlanList)

    def test_get_all(self):
        lst = plan.PlanList()
        self.assertEqual(1, len(lst.get_all(self.ctx)))

    def test_check_data_by_id(self):
        pl = plan.Plan().get_by_id(self.ctx, self.data[0]['id'])
        for key, value in self.data[0].items():
            self.assertEqual(value, getattr(pl, key))

    def test_check_data_by_uuid(self):
        pl = plan.Plan().get_by_uuid(self.ctx, self.data[0]['uuid'])
        for key, value in self.data[0].items():
            self.assertEqual(value, getattr(pl, key))
