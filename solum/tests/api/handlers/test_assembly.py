# -*- coding: utf-8 -*-
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
        db_obj = fakes.FakeAssembly()
        mock_registry.Assembly.get_by_uuid.return_value = db_obj
        handler = assembly_handler.AssemblyHandler(self.ctx)
        res = handler.update('test_id', data)
        self.assertEqual(db_obj.user_id, res.user_id)
        db_obj.save.assert_called_once_with(self.ctx)
        db_obj.update.assert_called_once_with(data)
        mock_registry.Assembly.get_by_uuid.assert_called_once_with(self.ctx,
                                                                   'test_id')

    @mock.patch('solum.worker.api.API.perform_action')
    @mock.patch('solum.common.solum_keystoneclient.KeystoneClientV3')
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
        trust_ctx = utils.dummy_context()
        trust_ctx.trust_id = '12345'
        mock_kc.return_value.create_trust_context.return_value = trust_ctx

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
            verb='build',
            build_id=8, name='nodeus', assembly_id=8,
            git_info=git_info, test_cmd=None,
            base_image_id='auto', source_format='heroku',
            source_creds_ref=None, image_format='qcow2')

        mock_kc.return_value.create_trust_context.assert_called_once_with()

    @mock.patch('solum.common.solum_keystoneclient.KeystoneClientV3')
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

    @mock.patch('solum.common.solum_keystoneclient.KeystoneClientV3')
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

    @mock.patch('solum.worker.api.API.perform_action')
    @mock.patch('solum.common.solum_keystoneclient.KeystoneClientV3')
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
        trust_ctx = utils.dummy_context()
        trust_ctx.trust_id = '12345'
        mock_kc.return_value.create_trust_context.return_value = trust_ctx

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
            verb='build',
            build_id=8, name='nodeus', assembly_id=8,
            git_info=git_info,
            test_cmd=None, base_image_id='auto', source_format='heroku',
            source_creds_ref='secret_ref_uri', image_format='qcow2')

        mock_kc.return_value.create_trust_context.assert_called_once_with()

    @mock.patch('solum.common.solum_keystoneclient.KeystoneClientV3')
    @mock.patch('solum.deployer.api.API.destroy')
    def test_delete(self, mock_deploy, mock_kc, mock_registry):
        db_obj = fakes.FakeAssembly()
        mock_registry.Assembly.get_by_uuid.return_value = db_obj
        handler = assembly_handler.AssemblyHandler(self.ctx)
        handler.delete('test_id')
        db_obj.save.assert_called_once_with(self.ctx)
        mock_registry.Assembly.get_by_uuid.assert_called_once_with(self.ctx,
                                                                   'test_id')
        mock_kc.return_value.delete_trust.assert_called_once_with(
            'trust_worthy')
        mock_deploy.assert_called_once_with(assem_id=db_obj.id)
        self.assertEqual(STATES.DELETING, db_obj.status)

    def test_trigger_workflow(self, mock_registry):
        trigger_id = 1
        artifacts = [{"name": "Test",
                      "artifact_type": "heroku",
                      "content": {"href": "https://github.com/some/project"},
                      "language_pack": "auto"}]
        db_obj = fakes.FakeAssembly()
        mock_registry.Assembly.get_by_trigger_id.return_value = db_obj
        plan_obj = fakes.FakePlan()
        mock_registry.Plan.get_by_id.return_value = plan_obj
        plan_obj.raw_content = {"artifacts": artifacts}
        handler = assembly_handler.AssemblyHandler(self.ctx)
        handler._build_artifact = mock.MagicMock()
        handler._context_from_trust_id = mock.MagicMock(return_value=self.ctx)
        handler.trigger_workflow(trigger_id)
        handler._build_artifact.assert_called_once_with(
            assem=db_obj,
            artifact=artifacts[0],
            commit_sha='',
            status_url=None,
            deploy_keys_ref=plan_obj.deploy_keys_uri)
        handler._context_from_trust_id.assert_called_once_with('trust_worthy')
        mock_registry.Assembly.get_by_trigger_id.assert_called_once_with(
            None, trigger_id)
        mock_registry.Plan.get_by_id.assert_called_once_with(self.ctx,
                                                             db_obj.plan_id)

    def test_trigger_workflow_verify_artifact_failed(self, mock_registry):
        trigger_id = 1
        artifacts = [{"name": "Test",
                      "artifact_type": "heroku",
                      "content": {"href": "https://github.com/some/project"},
                      "language_pack": "auto"}]
        db_obj = fakes.FakeAssembly()
        mock_registry.Assembly.get_by_trigger_id.return_value = db_obj
        plan_obj = fakes.FakePlan()
        mock_registry.Plan.get_by_id.return_value = plan_obj
        plan_obj.raw_content = {"artifacts": artifacts}
        handler = assembly_handler.AssemblyHandler(self.ctx)
        handler._build_artifact = mock.MagicMock()
        handler._verify_artifact = mock.MagicMock(return_value=False)
        handler._context_from_trust_id = mock.MagicMock(return_value=self.ctx)
        collab_url = 'https://api.github.com/repos/u/r/collaborators/foo'
        handler.trigger_workflow(trigger_id, collab_url=collab_url)
        assert not handler._build_artifact.called

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
