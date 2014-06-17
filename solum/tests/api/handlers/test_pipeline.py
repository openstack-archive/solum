#
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

import mock

from solum.api.handlers import pipeline_handler
from solum.tests import base
from solum.tests import fakes
from solum.tests import utils


@mock.patch('solum.objects.registry')
class TestPipelineHandler(base.BaseTestCase):
    def setUp(self):
        super(TestPipelineHandler, self).setUp()
        self.ctx = utils.dummy_context()

    def test_pipeline_get(self, mock_registry):
        mock_registry.return_value.Pipeline.get_by_uuid.return_value = {
            'plan_id': '1234'
        }
        handler = pipeline_handler.PipelineHandler(self.ctx)
        res = handler.get('test_id')
        self.assertIsNotNone(res)
        mock_registry.Pipeline.get_by_uuid.assert_called_once_with(
            self.ctx, 'test_id')

    def test_pipeline_get_all(self, mock_registry):
        mock_registry.PipelineList.get_all.return_value = {}
        handler = pipeline_handler.PipelineHandler(self.ctx)
        res = handler.get_all()
        self.assertIsNotNone(res)
        mock_registry.PipelineList.get_all.assert_called_once_with(self.ctx)

    def test_update(self, mock_registry):
        data = {'user_id': 'new_user_id',
                'plan_uuid': 'input_plan_uuid'}
        db_obj = fakes.FakePipeline()
        mock_registry.Pipeline.get_by_uuid.return_value = db_obj
        handler = pipeline_handler.PipelineHandler(self.ctx)
        res = handler.update('test_id', data)
        self.assertEqual(db_obj.user_id, res.user_id)
        db_obj.save.assert_called_once_with(self.ctx)
        db_obj.update.assert_called_once_with(data)
        mock_registry.Pipeline.get_by_uuid.assert_called_once_with(self.ctx,
                                                                   'test_id')

    @mock.patch('solum.common.solum_keystoneclient.KeystoneClientV3')
    def test_create(self, mock_kc, mock_registry):
        data = {'user_id': 'new_user_id',
                'uuid': 'input_uuid',
                'plan_uuid': 'input_plan_uuid'}

        db_obj = fakes.FakePipeline()
        mock_registry.Pipeline.return_value = db_obj
        fp = fakes.FakePlan()
        mock_registry.Plan.get_by_id.return_value = fp
        fp.raw_content = {
            'name': 'theplan',
            'artifacts': [{'name': 'nodeus',
                           'artifact_type': 'application.heroku',
                           'content': {
                               'href': 'https://example.com/ex.git'},
                           'language_pack': 'auto'}]}
        trust_ctx = utils.dummy_context()
        trust_ctx.trust_id = '12345'
        mock_kc.return_value.create_trust_context.return_value = trust_ctx

        handler = pipeline_handler.PipelineHandler(self.ctx)
        res = handler.create(data)
        db_obj.update.assert_called_once_with(data)
        db_obj.create.assert_called_once_with(self.ctx)
        self.assertEqual(db_obj, res)
        mock_kc.return_value.create_trust_context.assert_called_once_with()

    @mock.patch('solum.common.solum_keystoneclient.KeystoneClientV3')
    def test_delete(self, mock_kc, mock_registry):
        db_obj = fakes.FakePipeline()
        mock_registry.Pipeline.get_by_uuid.return_value = db_obj
        handler = pipeline_handler.PipelineHandler(self.ctx)
        handler.delete('test_id')
        db_obj.delete.assert_called_once_with(self.ctx)
        mock_registry.Pipeline.get_by_uuid.assert_called_once_with(self.ctx,
                                                                   'test_id')
        mock_kc.return_value.delete_trust.assert_called_once_with(
            'trust_worthy')

    def test_trigger_workflow(self, mock_registry):
        trigger_id = 1
        db_obj = fakes.FakePipeline()
        mock_registry.Pipeline.get_by_trigger_id.return_value = db_obj
        plan_obj = fakes.FakePlan()
        mock_registry.Plan.get_by_id.return_value = plan_obj
        handler = pipeline_handler.PipelineHandler(self.ctx)
        handler._execute_workbook = mock.MagicMock()
        handler._context_from_trust_id = mock.MagicMock(return_value=self.ctx)
        handler.trigger_workflow(trigger_id)
        handler._execute_workbook.assert_called_once_with(db_obj)
        handler._context_from_trust_id.assert_called_once_with('trust_worthy')
        mock_registry.Pipeline.get_by_trigger_id.assert_called_once_with(
            None, trigger_id)
