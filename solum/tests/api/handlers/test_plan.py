# Copyright (c) 2014 Rackspace Hosting
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

from unittest import mock

from solum.api.handlers import plan_handler
from solum.tests import base
from solum.tests import fakes
from solum.tests import utils


@mock.patch('solum.objects.registry')
class TestPlanHandler(base.BaseTestCase):
    def setUp(self):
        super(TestPlanHandler, self).setUp()
        self.ctx = utils.dummy_context()

    def test_plan_get(self, mock_registry):
        mock_registry.Plan.get_by_uuid.return_value = {}
        handler = plan_handler.PlanHandler(self.ctx)
        res = handler.get('test_id')
        self.assertIsNotNone(res)
        get_by_uuid = mock_registry.Plan.get_by_uuid
        get_by_uuid.assert_called_once_with(self.ctx, 'test_id')

    def test_plan_get_all(self, mock_registry):
        mock_registry.PlanList.get_all.return_value = {}
        handler = plan_handler.PlanHandler(self.ctx)
        res = handler.get_all()
        self.assertIsNotNone(res)
        mock_registry.PlanList.get_all.assert_called_once_with(self.ctx)

    def test_plan_update(self, mock_registry):
        data = {'user_id': 'new_user_id', 'name': 'new_name',
                'project_id': 'new_proj_id', 'uuid': 'new_uuid'}
        db_obj = fakes.FakePlan()
        mock_registry.Plan.get_by_uuid.return_value = db_obj
        db_obj.raw_content.update(data)
        to_update_data = {'name': data['name'],
                          'raw_content': db_obj.raw_content}
        handler = plan_handler.PlanHandler(self.ctx)
        handler.update('test_id', data)
        mock_registry.Plan.update_and_save.assert_called_once_with(
            self.ctx, 'test_id', to_update_data)

    @mock.patch('solum.common.clients.OpenStackClients.keystone')
    def test_plan_create(self, mock_kc, mock_registry):
        data = {'name': 'new_name',
                'uuid': 'input_uuid'}
        db_obj = fakes.FakePlan()
        mock_registry.Plan.return_value = db_obj
        handler = plan_handler.PlanHandler(self.ctx)
        res = handler.create(data)
        db_obj.create.assert_called_once_with(self.ctx)
        self.assertEqual(db_obj, res)

    @mock.patch('solum.common.clients.OpenStackClients.keystone')
    def test_plan_create_with_param(self, mock_kc, mock_registry):
        data = {'name': 'new_name',
                'uuid': 'input_uuid',
                'parameters': {'username': 'user_a'}}
        db_obj = fakes.FakePlan()
        param_obj = fakes.FakeParameter()
        mock_registry.Plan.return_value = db_obj
        mock_registry.Parameter.return_value = param_obj
        handler = plan_handler.PlanHandler(self.ctx)
        res = handler.create(data)
        db_obj.create.assert_called_once_with(self.ctx)
        param_obj.create.assert_called_once_with(self.ctx)
        self.assertEqual(db_obj, res)

    @mock.patch('solum.deployer.api.API.destroy_app')
    @mock.patch('solum.common.clients.OpenStackClients.keystone')
    def test_plan_delete(self, mock_kc, mock_destroy, mock_registry):
        db_obj = fakes.FakePlan()
        mock_registry.Plan.get_by_uuid.return_value = db_obj
        handler = plan_handler.PlanHandler(self.ctx)
        handler.delete('test_id')
        mock_destroy.assert_called_once_with(app_id=db_obj.id)
        mock_registry.Plan.get_by_uuid.assert_called_once_with(self.ctx,
                                                               'test_id')

    @mock.patch('solum.deployer.api.API.destroy_app')
    @mock.patch('solum.common.clients.OpenStackClients.keystone')
    def test_plan_delete_with_param(self, mock_kc, mock_destroy,
                                    mock_registry):
        db_obj = fakes.FakePlan()
        param_obj = fakes.FakeParameter()
        mock_registry.Plan.get_by_uuid.return_value = db_obj
        mock_registry.Parameter.get_by_plan_id.return_value = param_obj
        handler = plan_handler.PlanHandler(self.ctx)
        handler.delete('test_id')
        param_obj.destroy.assert_called_once_with(self.ctx)
        mock_registry.Plan.get_by_uuid.assert_called_once_with(self.ctx,
                                                               'test_id')
        mock_registry.Parameter.get_by_plan_id.assert_called_once_with(
            self.ctx, db_obj.id)
        mock_destroy.assert_called_once_with(app_id=db_obj.id)

    @mock.patch('solum.common.clients.OpenStackClients.keystone')
    def test_trigger_workflow_stage_select(self, mock_kc, mock_registry):
        trigger_id = 1
        plan_obj = fakes.FakePlan()
        artifacts = [{"name": "Test",
                      "artifact_type": "heroku",
                      "content": {"href": "https://github.com/some/project"},
                      "language_pack": "auto"}]
        plan_obj.raw_content = {"artifacts": artifacts}
        mock_registry.Plan.get_by_trigger_id.return_value = plan_obj
        handler = plan_handler.PlanHandler(self.ctx)
        handler._build_artifact = mock.MagicMock()
        handler.trigger_workflow(trigger_id, workflow=['unittest'])
        handler._build_artifact.assert_called_once_with(
            plan_obj,
            artifact=artifacts[0],
            commit_sha='',
            status_url=None,
            workflow=['unittest'],
            )
        mock_registry.Plan.get_by_trigger_id.assert_called_once_with(
            None, trigger_id)

    @mock.patch('solum.common.clients.OpenStackClients.keystone')
    def test_trigger_workflow_verify_artifact_failed(self, mock_kc,
                                                     mock_registry):

        trigger_id = 1
        plan_obj = fakes.FakePlan()
        artifacts = [{"name": "Test",
                      "artifact_type": "heroku",
                      "content": {"href": "https://github.com/some/project"},
                      "language_pack": "auto"}]
        plan_obj.raw_content = {"artifacts": artifacts}
        mock_registry.Plan.get_by_trigger_id.return_value = plan_obj
        handler = plan_handler.PlanHandler(self.ctx)
        handler._build_artifact = mock.MagicMock()
        handler._verify_artifact = mock.MagicMock(return_value=False)
        collab_url = 'https://api.github.com/repos/u/r/collaborators/foo'
        handler.trigger_workflow(trigger_id, collab_url=collab_url)
        assert not handler._build_artifact.called
