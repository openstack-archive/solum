# Copyright 2014 - Rackspace Hosting
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
from solum.objects.sqlalchemy import execution
from solum.tests import base
from solum.tests import utils


class TestExecution(base.BaseTestCase):
    def setUp(self):
        super(TestExecution, self).setUp()
        self.db = self.useFixture(utils.Database())
        self.ctx = utils.dummy_context()

        self.data = [{'pipeline_id': 'bla',
                      'uuid': 'ce43e347f0b0422825245b3e5f140a81cef6e65b'}]
        utils.create_models_from_data(execution.Execution, self.data, self.ctx)

    def test_objects_registered(self):
        self.assertIsNotNone(registry.Execution)
        self.assertIsNotNone(registry.ExecutionList)

    def test_get_all(self):
        lst = execution.ExecutionList()
        self.assertEqual(1, len(lst.get_all(self.ctx)))

    def test_check_data(self):
        pl = execution.Execution().get_by_id(self.ctx, self.data[0]['id'])
        for key, value in self.data[0].items():
            self.assertEqual(value, getattr(pl, key))
