# Copyright 2014 - Rackspace Hosting
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

import base64
import json
import os.path
from unittest import mock

from oslo_config import cfg
from oslo_utils import uuidutils

from solum.common import exception
from solum.i18n import _
from solum.privileged import rootwrap as priv_rootwrap
from solum.tests import base
from solum.tests import fakes
from solum.tests import utils
from solum.worker.handlers import shell as shell_handler


def mock_environment():
    return {
        'PATH': '/bin',
        'SOLUM_TASK_DIR': '/dev/null',
        'BUILD_ID': 'abcd',
        'PROJECT_ID': 1,
    }


def mock_git_info():
    return {
        'source_url': 'git://example.com/foo',
        'repo_token': '8765',
        'status_url': 'https://api.github.com/repos/u/r/statuses/SHA',
        'commit_sha': '1xxyz2'
    }


def mock_request_hdr(token):
    return {'Authorization': 'token ' + token,
            'Content-Type': 'application/json'}


def mock_req_pending_body(log_url):
    data = {'state': 'pending',
            'description': 'Solum says: Testing in progress',
            'target_url': log_url}
    return json.dumps(data)


def mock_req_success_body(log_url):
    data = {'state': 'success',
            'description': 'Solum says: Tests passed',
            'target_url': log_url}
    return json.dumps(data)


def mock_req_failure_body(log_url):
    data = {'state': 'failure',
            'description': 'Solum says: Tests failed',
            'target_url': log_url}
    return json.dumps(data)


def mock_http_response():
    return {'status': '401'}, ''


class HandlerTest(base.BaseTestCase):
    scenarios = [
        ('auto_lp_id',
         dict(base_image_id='auto',
              expected_img_id='auto',
              img_name='')),
        ('lp_id',
         dict(base_image_id='1-2-3-4',
              expected_img_id='TempUrl',
              img_name='tenant-name-ts-commit'))]

    def setUp(self):
        super(HandlerTest, self).setUp()
        self.ctx = utils.dummy_context()

    @mock.patch('solum.common.clients.OpenStackClients')
    def test_get_du_details_glance(self, mock_client):
        handler = shell_handler.Handler()
        du_id = 'dummy_du_id'
        cfg.CONF.set_override('image_storage', 'glance',
                              group='worker')
        fake_du = fakes.FakeImage()
        fake_du.id = 2
        fake_du.name = 'name'

        mock_glance = mock_client.return_value.glance
        mock_get = mock_glance.return_value.images.get
        mock_get.return_value = fake_du

        du_loc, du_name = handler.get_du_details(self.ctx, du_id)

        self.assertTrue(mock_get.called)
        self.assertTrue(du_loc, 2)
        self.assertTrue(du_name, 'name')

    @mock.patch('solum.common.clients.OpenStackClients')
    def test_get_du_details_GLANCE(self, mock_client):
        handler = shell_handler.Handler()
        du_id = 'dummy_du_id'
        cfg.CONF.set_override('image_storage', 'GLANCE',
                              group='worker')
        fake_du = fakes.FakeImage()
        fake_du.id = 2
        fake_du.name = 'name'

        mock_glance = mock_client.return_value.glance
        mock_get = mock_glance.return_value.images.get
        mock_get.return_value = fake_du

        du_loc, du_name = handler.get_du_details(self.ctx, du_id)

        self.assertTrue(mock_get.called)
        self.assertTrue(du_loc, 2)
        self.assertTrue(du_name, 'name')

    @mock.patch('solum.common.clients.OpenStackClients')
    def test_get_du_details_swift(self, mock_client):
        handler = shell_handler.Handler()
        du_id = 'dummy_du_id'
        cfg.CONF.set_override('image_storage', 'swift',
                              group='worker')
        try:
            handler.get_du_details(self.ctx, du_id)
            self.assertTrue(False)
        except exception.NotImplemented:
            self.assertTrue(True)

    @mock.patch('solum.worker.handlers.shell.Handler._get_environment')
    @mock.patch('solum.objects.registry')
    @mock.patch('solum.worker.handlers.shell.update_assembly_status')
    @mock.patch('solum.worker.handlers.shell.job_update_notification')
    @mock.patch('solum.deployer.api.API.deploy')
    @mock.patch('subprocess.Popen')
    @mock.patch('solum.TLS')
    @mock.patch('solum.worker.handlers.shell.get_lp_access_method')
    def test_build(self, mock_lp_access_method, mock_trace, mock_popen,
                   mock_deploy, mock_b_update, mock_uas,
                   mock_registry, mock_get_env):
        handler = shell_handler.Handler()
        fake_assembly = fakes.FakeAssembly()
        fake_glance_id = uuidutils.generate_uuid()
        fake_image_name = 'tenant-name-ts-commit'
        mock_registry.Assembly.get_by_id.return_value = fake_assembly
        fake_image = fakes.FakeImage()
        mock_registry.Image.get_lp_by_name_or_uuid.return_value = fake_image
        mock_popen.return_value.communicate.return_value = [
            'foo\ncreated_image_id=%s\ndocker_image_name=%s' %
            (fake_glance_id, fake_image_name), None]
        test_env = mock_environment()
        mock_get_env.return_value = test_env
        git_info = mock_git_info()

        handler.build(self.ctx, build_id=5, git_info=git_info,
                      name='new_app', base_image_id=self.base_image_id,
                      source_format='heroku', image_format='docker',
                      assembly_id=44, run_cmd=None)

        proj_dir = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                '..', '..', '..', '..'))
        script = os.path.join(proj_dir, 'contrib/lp-cedarish/docker/build-app')
        mock_popen.assert_called_once_with([script, 'git://example.com/foo',
                                            git_info['commit_sha'],
                                            'new_app', self.ctx.project_id,
                                            self.expected_img_id,
                                            self.img_name],
                                           env=test_env,
                                           stdout=-1)
        expected = [mock.call(self.ctx, 5, 'BUILDING',
                              description='Starting the image build',
                              assembly_id=44),
                    mock.call(self.ctx, 5, 'READY',
                              description='built successfully',
                              created_image_id=fake_glance_id,
                              docker_image_name=fake_image_name,
                              assembly_id=44)]

        self.assertEqual(expected, mock_b_update.call_args_list)

        expected = [mock.call(self.ctx, 44, 'BUILDING'),
                    mock.call(self.ctx, 44, 'BUILT')]
        self.assertEqual(expected, mock_uas.call_args_list)

        assert not mock_deploy.called

    @mock.patch('solum.worker.handlers.shell.Handler._get_environment')
    @mock.patch('solum.objects.registry')
    @mock.patch('solum.worker.handlers.shell.update_assembly_status')
    @mock.patch('solum.worker.handlers.shell.job_update_notification')
    @mock.patch('solum.deployer.api.API.deploy')
    @mock.patch('subprocess.Popen')
    @mock.patch('solum.TLS')
    @mock.patch('solum.worker.handlers.shell.get_lp_access_method')
    def test_build_swft(self, mock_lp_access_method, mock_trace, mock_popen,
                        mock_deploy,
                        mock_b_update, mock_uas,
                        mock_registry, mock_get_env):
        handler = shell_handler.Handler()
        fake_assembly = fakes.FakeAssembly()
        fake_glance_id = uuidutils.generate_uuid()
        fake_image_name = 'tenant-name-ts-commit'
        mock_registry.Assembly.get_by_id.return_value = fake_assembly
        fake_image = fakes.FakeImage()
        mock_registry.Image.get_by_uuid.return_value = fake_image
        mock_registry.Image.get_lp_by_name_or_uuid = fake_image

        cfg.CONF.api.operator_project_id = "abc"

        cfg.CONF.set_override('image_storage', 'swift',
                              group='worker')

        mock_popen.return_value.communicate.return_value = [
            'foo\ncreated_image_id=%s\ndocker_image_name=%s' %
            (fake_glance_id, fake_image_name)]
        test_env = mock_environment()
        mock_get_env.return_value = test_env
        git_info = mock_git_info()

        handler.build(self.ctx, build_id=5, git_info=git_info, name='new_app',
                      base_image_id=fake_image.base_image_id,
                      source_format='heroku', image_format='docker',
                      assembly_id=44, run_cmd=None)

        proj_dir = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                '..', '..', '..', '..'))
        script = os.path.join(proj_dir, 'contrib/lp-cedarish/docker/build-app')
        expected_loc = fake_image.external_ref
        expected_tag = fake_image.docker_image_name
        mock_popen.assert_called_once_with([script, 'git://example.com/foo',
                                            git_info['commit_sha'],
                                            'new_app', self.ctx.project_id,
                                            expected_loc, expected_tag],
                                           env=test_env,
                                           stdout=-1)
        expected = [mock.call(self.ctx, 5, 'BUILDING',
                              description='Starting the image build',
                              assembly_id=44),
                    mock.call(self.ctx, 5, 'READY',
                              description='built successfully',
                              created_image_id=fake_glance_id,
                              docker_image_name=fake_image_name,
                              assembly_id=44)]

        self.assertEqual(expected, mock_b_update.call_args_list)

        expected = [mock.call(self.ctx, 44, 'BUILDING'),
                    mock.call(self.ctx, 44, 'BUILT')]
        self.assertEqual(expected, mock_uas.call_args_list)

        assert not mock_deploy.called

    @mock.patch('solum.worker.handlers.shell.Handler._get_environment')
    @mock.patch('solum.objects.registry')
    @mock.patch('solum.worker.handlers.shell.update_assembly_status')
    @mock.patch('solum.worker.handlers.shell.job_update_notification')
    @mock.patch('solum.worker.handlers.shell.Handler._do_deploy')
    @mock.patch('subprocess.Popen')
    @mock.patch('ast.literal_eval')
    @mock.patch('solum.TLS')
    @mock.patch('solum.worker.handlers.shell.get_lp_access_method')
    def test_build_with_private_github_repo(
            self, mock_trace, mock_lp_access, mock_ast, mock_popen,
            mock_deploy, mock_uas, mock_b_update,
            mock_registry, mock_get_env):
        handler = shell_handler.Handler()
        fake_assembly = fakes.FakeAssembly()
        fake_glance_id = uuidutils.generate_uuid()
        fake_image_name = 'tenant-name-ts-commit'
        mock_registry.Assembly.get_by_id.return_value = fake_assembly
        fake_image = fakes.FakeImage()
        mock_registry.Image.get_lp_by_name_or_uuid.return_value = fake_image
        handler._update_assembly_status = mock.MagicMock()
        mock_popen.return_value.communicate.return_value = [
            'foo\ncreated_image_id=%s\ndocker_image_name=%s' %
            (fake_glance_id, fake_image_name), None]
        test_env = mock_environment()
        mock_get_env.return_value = test_env
        mock_ast.return_value = [{'source_url': 'git://example.com/foo',
                                  'private_key': 'some-private-key'}]
        git_info = mock_git_info()
        handler.launch_workflow(
            self.ctx, build_id=5, git_info=git_info,
            workflow=['unittest', 'build', 'deploy'], ports=[80],
            name='new_app', base_image_id=self.base_image_id,
            source_format='heroku', image_format='docker', assembly_id=44,
            test_cmd=None, run_cmd=None, du_id=None)

        proj_dir = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                '..', '..', '..', '..'))
        script = os.path.join(proj_dir, 'contrib/lp-cedarish/docker/build-app')
        mock_popen.assert_called_once_with([script, 'git://example.com/foo',
                                            git_info['commit_sha'],
                                            'new_app', self.ctx.project_id,
                                            self.expected_img_id,
                                            self.img_name],
                                           env=test_env, stdout=-1)
        expected = [mock.call(self.ctx, 5, 'BUILDING',
                              description='Starting the image build',
                              assembly_id=44),
                    mock.call(self.ctx, 5, 'READY',
                              description='built successfully',
                              created_image_id=fake_glance_id,
                              docker_image_name=fake_image_name,
                              assembly_id=44)]

        self.assertEqual(expected, mock_uas.call_args_list)

        expected = [mock.call(self.ctx, 44, 'BUILDING'),
                    mock.call(self.ctx, 44, 'BUILT')]
        self.assertEqual(expected, mock_b_update.call_args_list)

        expected = [mock.call(self.ctx, 44, [80], fake_glance_id,
                              fake_image_name
                              )]
        self.assertEqual(expected, mock_deploy.call_args_list)

    @mock.patch('solum.worker.handlers.shell.Handler._get_environment')
    @mock.patch('solum.objects.registry')
    @mock.patch('solum.worker.handlers.shell.job_update_notification')
    @mock.patch('solum.worker.handlers.shell.update_assembly_status')
    @mock.patch('solum.worker.handlers.shell.Handler._do_deploy')
    @mock.patch('subprocess.Popen')
    @mock.patch('shelve.open')
    @mock.patch('ast.literal_eval')
    @mock.patch('solum.TLS')
    def test_build_with_private_github_repo_with_shelve(
            self, mock_trace, mock_ast, mock_shelve, mock_popen,
            mock_deploy, mock_uas, mock_b_update, mock_registry,
            mock_get_env):
        handler = shell_handler.Handler()
        fake_assembly = fakes.FakeAssembly()
        fake_glance_id = uuidutils.generate_uuid()
        fake_image_name = 'tenant-name-ts-commit'
        mock_registry.Assembly.get_by_id.return_value = fake_assembly
        fake_image = fakes.FakeImage()
        mock_registry.Image.get_lp_by_name_or_uuid.return_value = fake_image
        handler._update_assembly_status = mock.MagicMock()
        mock_popen.return_value.communicate.return_value = [
            'foo\ncreated_image_id=%s\ndocker_image_name=%s' %
            (fake_glance_id, fake_image_name), None]
        test_env = mock_environment()
        mock_get_env.return_value = test_env
        cfg.CONF.api.system_param_store = 'local_file'
        cfg.CONF.api.system_param_file = 'some_file_path'
        cfg.CONF.api.operator_project_id = "abc"
        mock_shelve.return_value = mock.MagicMock()
        base64.b64decode = mock.MagicMock()
        mock_ast.return_value = [{'source_url': 'git://example.com/foo',
                                  'private_key': 'some-private-key'}]

        git_info = mock_git_info()
        handler.launch_workflow(
            self.ctx, build_id=5, git_info=git_info,
            workflow=['unitetst', 'build', 'deploy'], ports=[80],
            name='new_app', base_image_id=self.base_image_id,
            source_format='heroku', image_format='docker', assembly_id=44,
            test_cmd=None, run_cmd=None, du_id=None)

        proj_dir = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                '..', '..', '..', '..'))
        script = os.path.join(proj_dir, 'contrib/lp-cedarish/docker/build-app')
        # TODO(datsun180b): Determine if this commented line should be removed
        # since I can't seem to find anywhere in shell.py that writes to
        # shelve.
        # self.assertTrue(mock_shelve.call().__setitem__.called)
        mock_popen.assert_called_once_with([script, 'git://example.com/foo',
                                            git_info['commit_sha'],
                                            'new_app', self.ctx.project_id,
                                            self.expected_img_id,
                                            self.img_name],
                                           env=test_env, stdout=-1)
        expected = [mock.call(self.ctx, 5, 'BUILDING',
                              description='Starting the image build',
                              assembly_id=44),
                    mock.call(self.ctx, 5, 'READY',
                              description='built successfully',
                              created_image_id=fake_glance_id,
                              docker_image_name=fake_image_name,
                              assembly_id=44)]

        self.assertEqual(expected, mock_b_update.call_args_list)

        expected = [mock.call(self.ctx, 44, 'BUILDING'),
                    mock.call(self.ctx, 44, 'BUILT')]
        self.assertEqual(expected, mock_uas.call_args_list)

        expected = [mock.call(self.ctx, 44, [80], fake_glance_id,
                              fake_image_name
                              )]
        self.assertEqual(expected, mock_deploy.call_args_list)

    @mock.patch('solum.worker.handlers.shell.Handler._get_environment')
    @mock.patch('solum.objects.registry')
    @mock.patch('solum.worker.handlers.shell.job_update_notification')
    @mock.patch('solum.worker.handlers.shell.update_assembly_status')
    @mock.patch('subprocess.Popen')
    @mock.patch('solum.TLS')
    def test_build_fail(self, mock_trace, mock_popen, mock_uas,
                        mock_b_update,
                        mock_registry, mock_get_env):
        handler = shell_handler.Handler()
        fake_assembly = fakes.FakeAssembly()
        mock_registry.Assembly.get_by_id.return_value = fake_assembly
        fake_image = fakes.FakeImage()
        mock_registry.Image.get_lp_by_name_or_uuid.return_value = fake_image
        mock_popen.return_value.communicate.return_value = [
            'foo\ncreated_image_id=\n', None]
        test_env = mock_environment()
        mock_get_env.return_value = test_env
        git_info = mock_git_info()
        cfg.CONF.api.operator_project_id = "abc"

        handler.build(self.ctx, build_id=5, git_info=git_info, name='new_app',
                      base_image_id='auto', source_format='heroku',
                      image_format='docker', assembly_id=44, run_cmd=None)

        proj_dir = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                '..', '..', '..', '..'))
        script = os.path.join(proj_dir, 'contrib/lp-cedarish/docker/build-app')
        mock_popen.assert_called_once_with([script, 'git://example.com/foo',
                                            git_info['commit_sha'],
                                            'new_app', self.ctx.project_id,
                                            'auto',
                                            ''],
                                           env=test_env, stdout=-1)

        expected = [mock.call(self.ctx, 5, 'BUILDING',
                              description='Starting the image build',
                              assembly_id=44),
                    mock.call(self.ctx, 5, 'ERROR',
                              description='image not created',
                              assembly_id=44)]

        self.assertEqual(expected, mock_b_update.call_args_list)

        expected = [mock.call(self.ctx, 44, 'BUILDING'),
                    mock.call(self.ctx, 44, 'ERROR')]
        self.assertEqual(expected, mock_uas.call_args_list)

    @mock.patch('solum.worker.handlers.shell.Handler._get_environment')
    @mock.patch('solum.objects.registry')
    @mock.patch('solum.worker.handlers.shell.job_update_notification')
    @mock.patch('solum.worker.handlers.shell.update_assembly_status')
    @mock.patch('subprocess.Popen')
    @mock.patch('solum.TLS')
    def test_build_error(self, mock_trace, mock_popen, mock_uas,
                         mock_b_update,
                         mock_registry, mock_get_env):
        handler = shell_handler.Handler()
        fake_assembly = fakes.FakeAssembly()
        mock_registry.Assembly.get_by_id.return_value = fake_assembly
        fake_image = fakes.FakeImage()
        mock_registry.Image.get_lp_by_name_or_uuid.return_value = fake_image
        mock_popen.call.return_value = ValueError
        test_env = mock_environment()
        mock_get_env.return_value = test_env
        git_info = mock_git_info()
        cfg.CONF.api.operator_project_id = "abc"
        handler.build(self.ctx, build_id=5, git_info=git_info, name='new_app',
                      base_image_id=self.base_image_id, source_format='heroku',
                      image_format='docker', assembly_id=44, run_cmd=None)

        proj_dir = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                '..', '..', '..', '..'))
        script = os.path.join(proj_dir, 'contrib/lp-cedarish/docker/build-app')
        mock_popen.assert_called_once_with([script, 'git://example.com/foo',
                                            git_info['commit_sha'],
                                            'new_app', self.ctx.project_id,
                                            self.expected_img_id,
                                            self.img_name],
                                           env=test_env, stdout=-1)

        expected = [mock.call(self.ctx, 5, 'BUILDING',
                              description='Starting the image build',
                              assembly_id=44),
                    mock.call(self.ctx, 5, 'ERROR',
                              description='image not created',
                              assembly_id=44)]

        self.assertEqual(expected, mock_b_update.call_args_list)

        expected = [mock.call(self.ctx, 44, 'BUILDING'),
                    mock.call(self.ctx, 44, 'ERROR')]
        self.assertEqual(expected, mock_uas.call_args_list)

    @mock.patch('solum.worker.handlers.shell.Handler._get_environment')
    @mock.patch('solum.objects.registry')
    @mock.patch('subprocess.Popen')
    @mock.patch('solum.worker.handlers.shell.update_assembly_status')
    @mock.patch('solum.TLS')
    def test_unittest(self, mock_trace, mock_a_update, mock_popen,
                      mock_registry,
                      mock_get_env):
        handler = shell_handler.Handler()
        fake_assembly = fakes.FakeAssembly()
        mock_registry.Assembly.get_by_id.return_value = fake_assembly
        fake_image = fakes.FakeImage()
        mock_registry.Image.get_lp_by_name_or_uuid.return_value = fake_image
        test_env = mock_environment()
        mock_get_env.return_value = test_env
        mock_popen.return_value.wait.return_value = 0
        git_info = mock_git_info()
        cfg.CONF.api.operator_project_id = "abc"
        handler.unittest(self.ctx, build_id=5, name='new_app',
                         base_image_id=self.base_image_id,
                         source_format='chef', image_format='docker',
                         assembly_id=fake_assembly.id,
                         git_info=git_info, test_cmd='tox')

        proj_dir = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                '..', '..', '..', '..'))
        script = os.path.join(proj_dir,
                              'contrib/lp-chef/docker/unittest-app')
        mock_popen.assert_called_once_with([script, 'git://example.com/foo',
                                            git_info['commit_sha'],
                                            self.ctx.project_id,
                                            self.expected_img_id,
                                            self.img_name],
                                           env=test_env, stdout=-1)
        expected = [mock.call(self.ctx, 8, 'UNIT_TESTING'),
                    mock.call(self.ctx, 8, 'UNIT_TESTING_PASSED')]

        self.assertEqual(expected, mock_a_update.call_args_list)

    @mock.patch('solum.worker.handlers.shell.Handler._get_environment')
    @mock.patch('solum.objects.registry')
    @mock.patch('subprocess.Popen')
    @mock.patch('solum.worker.handlers.shell.update_assembly_status')
    @mock.patch('solum.TLS')
    def test_unittest_failure(self, mock_trace, mock_a_update, mock_popen,
                              mock_registry, mock_get_env):
        handler = shell_handler.Handler()
        fake_assembly = fakes.FakeAssembly()
        mock_registry.Assembly.get_by_id.return_value = fake_assembly
        fake_image = fakes.FakeImage()
        mock_registry.Image.get_lp_by_name_or_uuid.return_value = fake_image
        test_env = mock_environment()
        mock_get_env.return_value = test_env
        mock_popen.return_value.wait.return_value = 1
        git_info = mock_git_info()
        cfg.CONF.api.operator_project_id = "abc"

        handler.unittest(self.ctx, build_id=5, name='new_app',
                         assembly_id=fake_assembly.id,
                         base_image_id=self.base_image_id,
                         source_format='chef',
                         image_format='docker',
                         git_info=git_info, test_cmd='tox')

        proj_dir = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                '..', '..', '..', '..'))
        script = os.path.join(proj_dir,
                              'contrib/lp-chef/docker/unittest-app')
        mock_popen.assert_called_once_with([script, 'git://example.com/foo',
                                            git_info['commit_sha'],
                                            self.ctx.project_id,
                                            self.expected_img_id,
                                            self.img_name],
                                           env=test_env, stdout=-1)
        expected = [mock.call(self.ctx, 8, 'UNIT_TESTING'),
                    mock.call(self.ctx, 8, 'UNIT_TESTING_FAILED')]

        self.assertEqual(expected, mock_a_update.call_args_list)

    @mock.patch('solum.worker.handlers.shell.Handler._get_environment')
    @mock.patch('solum.objects.registry')
    @mock.patch('subprocess.Popen')
    @mock.patch('solum.worker.handlers.shell.job_update_notification')
    @mock.patch('solum.worker.handlers.shell.update_assembly_status')
    @mock.patch('solum.worker.handlers.shell.Handler._do_deploy')
    @mock.patch('solum.TLS')
    def test_unittest_build_deploy(self, mock_trace, mock_deploy,
                                   mock_a_update,
                                   mock_b_update, mock_popen, mock_registry,
                                   mock_get_env):
        handler = shell_handler.Handler()
        fake_assembly = fakes.FakeAssembly()
        fake_glance_id = uuidutils.generate_uuid()
        fake_image_name = 'tenant-name-ts-commit'
        mock_registry.Assembly.get_by_id.return_value = fake_assembly
        fake_image = fakes.FakeImage()
        mock_registry.Image.get_lp_by_name_or_uuid.return_value = fake_image
        mock_popen.return_value.wait.return_value = 0
        mock_popen.return_value.communicate.return_value = [
            'foo\ncreated_image_id=%s\ndocker_image_name=%s' %
            (fake_glance_id, fake_image_name), None]
        test_env = mock_environment()
        mock_get_env.return_value = test_env
        git_info = mock_git_info()
        cfg.CONF.api.operator_project_id = "abc"
        handler.launch_workflow(
            self.ctx, build_id=5, git_info=git_info,
            workflow=['unittest', 'build', 'deploy'], ports=[80],
            name='new_app', base_image_id=self.base_image_id,
            source_format='heroku', image_format='docker', assembly_id=44,
            test_cmd='faketests', run_cmd=None, du_id=None)

        proj_dir = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                '..', '..', '..', '..'))
        util_dir = os.path.join(proj_dir, 'contrib', 'lp-cedarish', 'docker')
        u_script = os.path.join(util_dir, 'unittest-app')
        b_script = os.path.join(util_dir, 'build-app')

        expected = [
            mock.call([u_script, 'git://example.com/foo',
                       git_info['commit_sha'],
                       self.ctx.project_id, self.expected_img_id,
                       self.img_name], env=test_env,
                      stdout=-1),
            mock.call([b_script, 'git://example.com/foo',
                       git_info['commit_sha'], 'new_app',
                       self.ctx.project_id, self.expected_img_id,
                       self.img_name], env=test_env,
                      stdout=-1)]
        self.assertEqual(expected, mock_popen.call_args_list)

        expected = [mock.call(self.ctx, 5, 'BUILDING',
                              description='Starting the image build',
                              assembly_id=44),
                    mock.call(self.ctx, 5, 'READY',
                              description='built successfully',
                              created_image_id=fake_glance_id,
                              docker_image_name=fake_image_name,
                              assembly_id=44)]
        self.assertEqual(expected, mock_b_update.call_args_list)

        expected = [mock.call(self.ctx, 44, 'UNIT_TESTING'),
                    mock.call(self.ctx, 44, 'UNIT_TESTING_PASSED'),
                    mock.call(self.ctx, 44, 'BUILDING'),
                    mock.call(self.ctx, 44, 'BUILT')]
        self.assertEqual(expected, mock_a_update.call_args_list)

        expected = [mock.call(self.ctx, 44, [80], fake_glance_id,
                              fake_image_name
                              )]
        self.assertEqual(expected, mock_deploy.call_args_list)

    @mock.patch('solum.worker.handlers.shell.Handler._do_build')
    @mock.patch('solum.worker.handlers.shell.Handler._get_environment')
    @mock.patch('subprocess.Popen')
    @mock.patch('solum.worker.handlers.shell.update_assembly_status')
    @mock.patch('solum.objects.registry')
    @mock.patch('solum.TLS')
    def test_unittest_no_build(self, mock_trace,
                               mock_registry, mock_a_update, mock_popen,
                               mock_get_env, mock_do_build):
        handler = shell_handler.Handler()
        mock_assembly = mock.MagicMock()
        mock_registry.Assembly.get_by_id.return_value = mock_assembly
        fake_image = fakes.FakeImage()
        mock_registry.Image.get_lp_by_name_or_uuid.return_value = fake_image
        mock_popen.return_value.wait.return_value = 1
        test_env = mock_environment()
        mock_get_env.return_value = test_env
        git_info = mock_git_info()
        cfg.CONF.api.operator_project_id = "abc"
        handler.launch_workflow(
            self.ctx, build_id=5, git_info=git_info, name='new_app',
            base_image_id=self.base_image_id, source_format='chef',
            image_format='docker', assembly_id=44, ports=[80],
            test_cmd='faketests', run_cmd=None, workflow=['unittest', 'build'],
            du_id=None)

        proj_dir = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                '..', '..', '..', '..'))
        util_dir = os.path.join(proj_dir, 'contrib', 'lp-chef', 'docker')
        u_script = os.path.join(util_dir, 'unittest-app')

        expected = [
            mock.call([u_script, 'git://example.com/foo',
                       git_info['commit_sha'],
                       self.ctx.project_id, self.expected_img_id,
                       self.img_name], env=test_env,
                      stdout=-1)]
        self.assertEqual(expected, mock_popen.call_args_list)

        expected = [mock.call(self.ctx, 44, 'UNIT_TESTING'),
                    mock.call(self.ctx, 44, 'UNIT_TESTING_FAILED')]
        self.assertEqual(expected, mock_a_update.call_args_list)

        assert not mock_do_build.called


class HandlerUtilityTest(base.BaseTestCase):
    def setUp(self):
        super(HandlerUtilityTest, self).setUp()
        self.ctx = utils.dummy_context()

    @mock.patch('solum.worker.handlers.shell.LOG')
    def test_echo(self, fake_LOG):
        shell_handler.Handler().echo({}, 'foo')
        fake_LOG.debug.assert_called_once_with(_('%s') % 'foo')

    @mock.patch('solum.worker.handlers.shell.get_parameter_by_assem_id')
    @mock.patch('builtins.open')
    @mock.patch('os.makedirs')
    def test_get_parameter_files(self, mock_mkdirs, mock_open, mock_param):
        mock_param.return_value = {"user_params": {'key': 'ab"cd'}}
        fake_build_id = '1-2-3-4'
        cfg.CONF.set_override('param_file_path', '/tmp/test', group='worker')
        path = '/tmp/test/' + fake_build_id
        handler = shell_handler.Handler()

        handler._get_parameter_env(self.ctx, 'git://example.com/foo',
                                   8, fake_build_id)

        mock_mkdirs.assert_called_once_with(path, 0o700)
        expected = [mock.call(path + '/user_params', 'w'),
                    mock.call(path + '/solum_params', 'w')]
        self.assertEqual(expected, mock_open.call_args_list)

        mock_file = mock_open.return_value.__enter__.return_value
        expected_params = [mock.call('#!/bin/bash\n'),
                           mock.call('export key="ab\\"cd"\n'),
                           mock.call('#!/bin/bash\n')]
        self.assertEqual(expected_params, mock_file.write.call_args_list)


class TestNotifications(base.BaseTestCase):
    def setUp(self):
        super(TestNotifications, self).setUp()
        self.ctx = utils.dummy_context()
        self.db = self.useFixture(utils.Database())

    @mock.patch('solum.conductor.api.API.update_assembly')
    @mock.patch('solum.objects.registry')
    def test_update_assembly_status(self, mock_registry, mock_uas):
        mock_assembly = mock.MagicMock()
        mock_registry.Assembly.get_by_id.return_value = mock_assembly
        shell_handler.update_assembly_status(self.ctx, '1234',
                                             'BUILDING')
        self.assertEqual(mock_registry.Assembly.get_by_id.call_count, 0)
        self.assertEqual(mock_registry.save.call_count, 0)
        self.assertEqual(mock_uas.call_count, 1)

    @mock.patch('solum.conductor.api.API.update_assembly')
    @mock.patch('solum.objects.registry')
    def test_update_assembly_status_pass(self, mock_registry, mock_uas):
        shell_handler.update_assembly_status(self.ctx, None,
                                             'BUILDING')
        self.assertEqual(mock_registry.call_count, 0)


class TestBuildCommand(base.BaseTestCase):
    scenarios = [
        ('docker',
         dict(source_format='heroku', image_format='docker',
              base_image_id='auto', artifact_type=None,
              expect_b='lp-cedarish/docker/build-app',
              expect_u='lp-cedarish/docker/unittest-app')),
        ('dockerfile',
         dict(source_format='dockerfile', image_format='docker',
              base_image_id='auto', artifact_type=None,
              expect_b='lp-dockerfile/docker/build-app',
              expect_u='lp-dockerfile/docker/unittest-app')),
        ('chef',
         dict(source_format='chef', image_format='docker',
              base_image_id='xyz', artifact_type=None,
              expect_b='lp-chef/docker/build-app',
              expect_u='lp-chef/docker/unittest-app'))]

    def test_build_cmd(self):
        ctx = utils.dummy_context()
        handler = shell_handler.Handler()
        cmd = handler._get_build_command(ctx,
                                         'build',
                                         'http://example.com/a.git',
                                         'testa',
                                         self.base_image_id,
                                         self.source_format,
                                         self.image_format, '',
                                         self.artifact_type)
        self.assertIn(self.expect_b, cmd[0])
        self.assertEqual('http://example.com/a.git', cmd[1])
        self.assertEqual('testa', cmd[3])
        self.assertEqual(ctx.project_id, cmd[4])
        if self.base_image_id == 'auto' and self.image_format == 'qcow2':
            self.assertEqual('cedarish', cmd[5])
        else:
            self.assertEqual(self.base_image_id, cmd[5])

    def test_unittest_cmd(self):
        ctx = utils.dummy_context()
        handler = shell_handler.Handler()
        cmd = handler._get_build_command(ctx,
                                         'unittest',
                                         'http://example.com/a.git',
                                         'testa',
                                         self.base_image_id,
                                         self.source_format,
                                         self.image_format, 'asdf',
                                         self.artifact_type)
        self.assertIn(self.expect_u, cmd[0])
        self.assertEqual('http://example.com/a.git', cmd[1])
        self.assertEqual('asdf', cmd[2])
        self.assertEqual(ctx.project_id, cmd[3])


class TestLanguagePackBuildCommand(base.BaseTestCase):
    def setUp(self):
        super(TestLanguagePackBuildCommand, self).setUp()
        self.ctx = utils.dummy_context()

    def test_languagepack_build_cmd(self):
        ctx = utils.dummy_context()
        handler = shell_handler.Handler()
        cmd = handler._get_build_command(ctx,
                                         'build',
                                         'http://example.com/a.git',
                                         'testa',
                                         'auto',
                                         'heroku',
                                         'docker', '',
                                         'language_pack')
        self.assertIn('lp-cedarish/docker/build-lp', cmd[0])
        self.assertEqual('http://example.com/a.git', cmd[1])
        self.assertEqual('testa', cmd[2])
        self.assertEqual(ctx.project_id, cmd[3])

    @mock.patch('solum.worker.handlers.shell.Handler._get_environment')
    @mock.patch('solum.objects.registry')
    @mock.patch('solum.worker.handlers.shell.update_lp_status')
    @mock.patch.object(priv_rootwrap, 'execute')
    @mock.patch('solum.TLS')
    def test_build_lp(self, mock_trace, mock_execute, mock_ui,
                      mock_registry, mock_get_env):
        handler = shell_handler.Handler()
        fake_image = fakes.FakeImage()
        fake_glance_id = uuidutils.generate_uuid()
        fake_image_name = 'tenant-name-ts-commit'
        mock_registry.Image.get_lp_by_name_or_uuid.return_value = fake_image
        mock_execute.return_value = (
            'foo\nimage_external_ref=%s\ndocker_image_name=%s\n' %
            (fake_glance_id, fake_image_name), None)
        test_env = mock_environment()
        mock_get_env.return_value = test_env
        git_info = mock_git_info()
        cfg.CONF.api.operator_project_id = "abc"
        handler.build_lp(self.ctx, image_id=5, git_info=git_info,
                         name='lp_name', source_format='heroku',
                         image_format='docker', artifact_type='language_pack',
                         lp_params='')

        proj_dir = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                '..', '..', '..', '..'))
        script = os.path.join(proj_dir, 'contrib/lp-cedarish/docker/build-lp')
        mock_execute.assert_called_once_with(
            script, 'git://example.com/foo',
            'lp_name', self.ctx.project_id,
            env_variables=test_env,
            run_as_root=True,
        )

        expected = [mock.call(self.ctx, 5, 'lp_name', 'BUILDING'),
                    mock.call(self.ctx, 5, 'lp_name', 'READY',
                              fake_glance_id, fake_image_name)]
        self.assertEqual(expected, mock_ui.call_args_list)
