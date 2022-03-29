# Copyright 2015 - Rackspace US, Inc.
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
from solum.objects.sqlalchemy import workflow
from solum.tests import base
from solum.tests import utils


class TestWorkflow(base.BaseTestCase):
    def setUp(self):
        super(TestWorkflow, self).setUp()
        self.db = self.useFixture(utils.Database())
        self.ctx = utils.dummy_context()
        self.data = [self._get_data(self.ctx.project_id)]
        utils.create_models_from_data(workflow.Workflow, self.data, self.ctx)

    def _get_data(self, project_id):

        source = dict()
        source['repository'] = "https://github.com"
        source['revision'] = "master"

        workflow = dict()
        workflow["test_cmd"] = "./unit_tests.sh"
        workflow["run_cmd"] = "python app.py"

        jsondata = dict()
        jsondata['source'] = source
        jsondata['config'] = workflow
        jsondata['actions'] = ["test", "build", "deploy"]
        jsondata['project_id'] = project_id
        jsondata['user_id'] = 'fred'
        jsondata['id'] = '123'
        return jsondata

    def test_objects_registered(self):
        self.assertTrue(registry.Workflow)
        self.assertTrue(registry.WorkflowList)

    def test_get_all(self):
        lst = workflow.WorkflowList()
        self.assertEqual(1, len(lst.get_all(self.ctx)))

    def test_check_data_by_id(self):
        foundwf = workflow.Workflow().get_by_id(self.ctx, self.data[0]['id'])
        for key, value in self.data[0].items():
            self.assertEqual(value, getattr(foundwf, key))

    def test_check_data_by_uuid(self):
        foundwf = workflow.Workflow().get_by_uuid(self.ctx, self.data[0]['id'])
        for key, value in self.data[0].items():
            self.assertEqual(value, getattr(foundwf, key))
