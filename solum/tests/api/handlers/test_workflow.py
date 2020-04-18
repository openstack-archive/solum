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

from oslo_config import fixture as config

from solum.api import auth
from solum.api.handlers import workflow_handler
from solum.tests import base
from solum.tests import fakes
from solum.tests import utils


@mock.patch('solum.objects.registry')
class TestWorkflowHandler(base.BaseTestCase):
    def setUp(self):
        super(TestWorkflowHandler, self).setUp()
        self.ctx = utils.dummy_context()
        self.CONF = self.useFixture(config.Config())
        self.CONF.config(www_authenticate_uri='http://fakeidentity.com',
                         group=auth.OPT_GROUP_NAME)
        self.CONF.config(keystone_version='3')

    def test_workflow_get(self, mock_registry):
        mock_registry.return_value.Workflow.get_by_uuid.return_value = {
            'app_id': '1234'
        }
        handler = workflow_handler.WorkflowHandler(self.ctx)
        res = handler.get('test_id')
        self.assertIsNotNone(res)
        get_by_uuid = mock_registry.Workflow.get_by_uuid
        get_by_uuid.assert_called_once_with(self.ctx, 'test_id')

    def test_workflow_get_all(self, mock_reg):
        mock_reg.WorkflowList.get_all.return_value = {}
        handler = workflow_handler.WorkflowHandler(self.ctx)
        res = handler.get_all(app_id='123')
        self.assertIsNotNone(res)
        mock_reg.WorkflowList.get_all.assert_called_once_with(self.ctx,
                                                              app_id='123')

    def test_delete(self, mock_registry):
        db_obj = fakes.FakeWorkflow()
        mock_registry.Workflow.get_by_uuid.return_value = db_obj
        handler = workflow_handler.WorkflowHandler(self.ctx)
        handler.delete('test_id')
        mock_registry.Workflow.get_by_uuid.assert_called_once_with(self.ctx,
                                                                   'test_id')

    @mock.patch('solum.worker.api.API.build_app')
    @mock.patch('solum.objects.sqlalchemy.workflow.Workflow.insert')
    def test_create(self, mock_wf_insert, mock_pa, mock_registry):

        app_obj = fakes.FakeApp()
        app_id = app_obj.id
        test_cmd = app_obj.workflow_config['test_cmd']
        run_cmd = app_obj.workflow_config['run_cmd']
        mock_registry.App.get_by_id.return_value = app_obj

        workflow_data = {"app_id": app_id,
                         "source": app_obj.source,
                         "config": app_obj.workflow_config,
                         "actions": app_obj.trigger_actions}

        fp = fakes.FakePlan()
        mock_registry.Plan.return_value = fp

        fa = fakes.FakeAssembly()
        fa.plan_uuid = fp.uuid
        mock_registry.Assembly.return_value = fa

        wf_obj = fakes.FakeWorkflow()
        wf_obj.app_id = app_obj.id
        wf_obj.assembly = fa.id
        mock_registry.Workflow.return_value = wf_obj

        fi = fakes.FakeImage()
        mock_registry.Image.return_value = fi

        handler = workflow_handler.WorkflowHandler(self.ctx)

        res = handler.create(workflow_data, commit_sha='master', status_url='',
                             du_id='')
        self.assertEqual(wf_obj, res)
        git_info = {
            'source_url': app_obj.source['repository'],
            'commit_sha': app_obj.source['revision'],
            'repo_token': app_obj.source['repo_token'],
            'private': app_obj.source['private'],
            'private_ssh_key': app_obj.source['private_ssh_key'],
            'status_url': '',
        }
        mock_pa.assert_called_once_with(
            verb='launch_workflow', workflow=['unittest', 'build', 'deploy'],
            build_id=fa.id, name=fi.name, assembly_id=fa.id,
            git_info=git_info, test_cmd=test_cmd, ports=app_obj.ports,
            base_image_id=fi.base_image_id,
            source_format=fi.source_format,
            image_format=fi.image_format, run_cmd=run_cmd, du_id='')
