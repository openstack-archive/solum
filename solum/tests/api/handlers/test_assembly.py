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
from solum.api.handlers import assembly_handler
from solum.common import exception
from solum.common import repo_utils
from solum.objects import assembly
from solum.tests import base
from solum.tests import fakes
from solum.tests import utils


STATES = assembly.States


@mock.patch('solum.objects.registry')
class TestAssemblyHandler(base.BaseTestCase):
    def setUp(self):
        super(TestAssemblyHandler, self).setUp()
        self.ctx = utils.dummy_context()
        self.CONF = self.useFixture(config.Config())
        self.CONF.config(www_authenticate_uri='http://fakeidentity.com',
                         group=auth.OPT_GROUP_NAME)
        self.CONF.config(keystone_version='3')

    def test_assembly_get(self, mock_registry):
        mock_registry.return_value.Assembly.get_by_uuid.return_value = {
            'plan_id': '1234'
        }
        handler = assembly_handler.AssemblyHandler(self.ctx)
        res = handler.get('test_id')
        self.assertIsNotNone(res)
        get_by_uuid = mock_registry.Assembly.get_by_uuid
        get_by_uuid.assert_called_once_with(self.ctx, 'test_id')

    def test_assembly_get_all(self, mock_registry):
        mock_registry.AssemblyList.get_all.return_value = {}
        handler = assembly_handler.AssemblyHandler(self.ctx)
        res = handler.get_all()
        self.assertIsNotNone(res)
        mock_registry.AssemblyList.get_all.assert_called_once_with(self.ctx)

    def test_update(self, mock_registry):
        data = {'user_id': 'new_user_id',
                'plan_uuid': 'input_plan_uuid'}
        handler = assembly_handler.AssemblyHandler(self.ctx)
        handler.update('test_id', data)
        mock_registry.Assembly.update_and_save.assert_called_once_with(
            self.ctx, 'test_id', data)

    @mock.patch('solum.worker.api.API.build_app')
    @mock.patch('solum.common.clients.OpenStackClients.keystone')
    def test_create(self, mock_kc, mock_pa, mock_registry):
        data = {'user_id': 'new_user_id',
                'uuid': 'input_uuid',
                'plan_uuid': 'input_plan_uuid'}

        db_obj = fakes.FakeAssembly()
        mock_registry.Assembly.return_value = db_obj
        fp = fakes.FakePlan()
        mock_registry.Plan.get_by_id.return_value = fp
        fp.raw_content = {
            'name': 'theplan',
            'artifacts': [{'name': 'nodeus',
                           'artifact_type': 'heroku',
                           'content': {'private': False,
                                       'href': 'https://example.com/ex.git'},
                           'language_pack': 'auto'}]}

        mock_registry.Image.return_value = fakes.FakeImage()

        handler = assembly_handler.AssemblyHandler(self.ctx)
        res = handler.create(data)
        db_obj.update.assert_called_once_with(data)
        db_obj.create.assert_called_once_with(self.ctx)
        self.assertEqual(db_obj, res)
        git_info = {
            'source_url': "https://example.com/ex.git",
            'commit_sha': '',
            'repo_token': None,
            'status_url': None,
        }
        mock_pa.assert_called_once_with(
            verb='launch_workflow', workflow=['unittest', 'build', 'deploy'],
            build_id=8, name='nodeus', assembly_id=8,
            git_info=git_info, test_cmd=None, ports=[80],
            base_image_id='auto', source_format='heroku',
            image_format='qcow2', run_cmd=None)

    @mock.patch('solum.common.clients.OpenStackClients.keystone')
    def test_create_with_username_in_ctx(self, mock_kc, mock_registry):
        data = {'plan_uuid': 'input_plan_uuid'}

        db_obj = fakes.FakeAssembly()
        mock_registry.Assembly.return_value = db_obj
        fp = fakes.FakePlan()
        mock_registry.Plan.get_by_id.return_value = fp
        fp.raw_content = {'name': 'theplan'}

        handler = assembly_handler.AssemblyHandler(self.ctx)
        res = handler.create(data)

        self.assertEqual(res.username, self.ctx.user_name)

    @mock.patch('solum.common.clients.OpenStackClients.keystone')
    def test_create_without_username_in_ctx(self, mock_kc, mock_registry):
        data = {'plan_uuid': 'input_plan_uuid'}

        ctx = utils.dummy_context()
        ctx.user_name = ''
        db_obj = fakes.FakeAssembly()
        mock_registry.Assembly.return_value = db_obj
        fp = fakes.FakePlan()
        mock_registry.Plan.get_by_id.return_value = fp
        fp.raw_content = {'name': 'theplan'}

        handler = assembly_handler.AssemblyHandler(ctx)
        res = handler.create(data)

        self.assertEqual(res.username, '')

    @mock.patch('solum.worker.api.API.build_app')
    @mock.patch('solum.common.clients.OpenStackClients.keystone')
    def test_create_with_private_github_repo(self, mock_kc, mock_pa,
                                             mock_registry):
        data = {'user_id': 'new_user_id',
                'uuid': 'input_uuid',
                'plan_uuid': 'input_plan_uuid'}

        db_obj = fakes.FakeAssembly()
        mock_registry.Assembly.return_value = db_obj
        fp = fakes.FakePlan()
        mock_registry.Plan.get_by_id.return_value = fp
        fp.raw_content = {
            'name': 'theplan',
            'artifacts': [{'name': 'nodeus',
                           'artifact_type': 'heroku',
                           'content': {'private': True,
                                       'href': 'https://example.com/ex.git',
                                       'public_key': 'ssh-rsa abc'},
                           'language_pack': 'auto'}]}
        fp.deploy_keys_uri = 'secret_ref_uri'
        mock_registry.Image.return_value = fakes.FakeImage()

        handler = assembly_handler.AssemblyHandler(self.ctx)
        res = handler.create(data)
        db_obj.update.assert_called_once_with(data)
        db_obj.create.assert_called_once_with(self.ctx)
        self.assertEqual(db_obj, res)
        git_info = {
            'source_url': "https://example.com/ex.git",
            'commit_sha': '',
            'repo_token': None,
            'status_url': None,
        }
        mock_pa.assert_called_once_with(
            verb='launch_workflow', workflow=['unittest', 'build', 'deploy'],
            build_id=8, name='nodeus', assembly_id=8,
            git_info=git_info, ports=[80],
            test_cmd=None, base_image_id='auto', source_format='heroku',
            image_format='qcow2', run_cmd=None)

    @mock.patch('solum.common.clients.OpenStackClients.keystone')
    @mock.patch('solum.deployer.api.API.destroy_assembly')
    @mock.patch('solum.conductor.api.API.update_assembly')
    def test_delete(self, mock_cond, mock_deploy, mock_kc, mock_registry):
        db_obj = fakes.FakeAssembly()
        mock_registry.Assembly.get_by_uuid.return_value = db_obj
        handler = assembly_handler.AssemblyHandler(self.ctx)
        handler.delete('test_id')
        mock_registry.Assembly.get_by_uuid.assert_called_once_with(self.ctx,
                                                                   'test_id')
        mock_cond.assert_called_once_with(db_obj.id, {'status': 'DELETING'})
        mock_deploy.assert_called_once_with(assem_id=db_obj.id)

    @mock.patch('httplib2.Http.request')
    def test_verify_artifact_raise_exp(self, http_mock, mock_registry):
        artifact = {"name": "Test",
                    "artifact_type": "heroku",
                    "content": {"href": "https://github.com/some/project"},
                    "language_pack": "auto",
                    "repo_token": "abcd"}
        http_mock.return_value = ({'status': '404'}, '')  # Not a collaborator
        collab_url = 'https://api.github.com/repos/u/r/collaborators/foo'
        self.assertRaises(exception.RequestForbidden,
                          repo_utils.verify_artifact,
                          artifact, collab_url)
