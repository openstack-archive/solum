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
from solum.objects.sqlalchemy import execution
from solum.objects.sqlalchemy import pipeline
from solum.tests import base
from solum.tests import utils


class TestPipeline(base.BaseTestCase):
    def setUp(self):
        super(TestPipeline, self).setUp()
        self.db = self.useFixture(utils.Database())
        self.ctx = utils.dummy_context()

        self.data = [{'project_id': self.ctx.tenant,
                      'uuid': 'ce43e347f0b0422825245b3e5f140a81cef6e65b',
                      'user_id': 'fred',
                      'name': 'pipeline1',
                      'description': 'test pipeline',
                      'trigger_id': 'trigger-uuid-1234',
                      'tags': 'pipeline tags',
                      'plan_id': 'plan_id_1'}]
        utils.create_models_from_data(pipeline.Pipeline, self.data, self.ctx)

    def test_objects_registered(self):
        self.assertTrue(registry.Pipeline)
        self.assertTrue(registry.PipelineList)

    def test_get_all(self):
        lst = pipeline.PipelineList()
        self.assertEqual(1, len(lst.get_all(self.ctx)))

    def test_check_data(self):
        ta = pipeline.Pipeline().get_by_id(self.ctx, self.data[0]['id'])
        for key, value in self.data[0].items():
            self.assertEqual(value, getattr(ta, key))

    def test_check_data_by_trigger_id(self):
        ta = pipeline.Pipeline().get_by_trigger_id(self.ctx, self.data[0][
            'trigger_id'])
        for key, value in self.data[0].items():
            self.assertEqual(value, getattr(ta, key))

    def test_last_execution(self):
        ta = pipeline.Pipeline().get_by_id(self.ctx, self.data[0]['id'])
        # add executions
        ex1 = execution.Execution()
        ex1.uuid = 'first'
        ex1.pipeline_id = ta.id
        ex1.create(self.ctx)

        ex2 = execution.Execution()
        ex2.uuid = 'second'
        ex2.pipeline_id = ta.id
        ex2.create(self.ctx)

        extest = ta.last_execution()
        self.assertEqual('second', extest.uuid)

    def test_last_execution_none(self):
        ta = pipeline.Pipeline().get_by_id(self.ctx, self.data[0]['id'])
        extest = ta.last_execution()
        self.assertIsNone(extest)
