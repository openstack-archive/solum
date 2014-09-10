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

import json
import os.path
import uuid

import mock

from solum.openstack.common.gettextutils import _
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
        'status_token': '8765',
        'status_url': 'https://api.github.com/repos/u/r/statuses/SHA'
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
    def setUp(self):
        super(HandlerTest, self).setUp()
        self.ctx = utils.dummy_context()

    @mock.patch('solum.worker.handlers.shell.LOG')
    def test_echo(self, fake_LOG):
        shell_handler.Handler().echo({}, 'foo')
        fake_LOG.debug.assert_called_once_with(_('%s') % 'foo')

    @mock.patch('solum.worker.handlers.shell.Handler._get_environment')
    @mock.patch('solum.objects.registry')
    @mock.patch('solum.conductor.api.API.build_job_update')
    @mock.patch('solum.deployer.api.API.deploy')
    @mock.patch('subprocess.Popen')
    def test_build(self, mock_popen, mock_deploy, mock_b_update, mock_registry,
                   mock_get_env):
        handler = shell_handler.Handler()
        fake_assembly = fakes.FakeAssembly()
        fake_glance_id = str(uuid.uuid4())
        mock_registry.Assembly.get_by_id.return_value = fake_assembly
        mock_popen.return_value.communicate.return_value = [
            'foo\ncreated_image_id=%s' % fake_glance_id, None]
        test_env = mock_environment()
        mock_get_env.return_value = test_env
        git_info = mock_git_info()
        handler.build(self.ctx, build_id=5, git_info=git_info,
                      name='new_app', base_image_id='1-2-3-4',
                      source_format='heroku', image_format='docker',
                      assembly_id=44, test_cmd=None)

        proj_dir = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                '..', '..', '..', '..'))
        script = os.path.join(proj_dir, 'contrib/lp-cedarish/docker/build-app')
        mock_popen.assert_called_once_with([script, 'git://example.com/foo',
                                            'new_app', self.ctx.tenant,
                                            '1-2-3-4'],
                                           env=test_env, stdout=-1)
        expected = [mock.call(5, 'BUILDING', 'Starting the image build',
                              None, 44),
                    mock.call(5, 'COMPLETE', 'built successfully',
                              fake_glance_id, 44)]

        self.assertEqual(expected, mock_b_update.call_args_list)

        expected = [mock.call(assembly_id=44, image_id=fake_glance_id)]
        self.assertEqual(expected, mock_deploy.call_args_list)

    @mock.patch('solum.worker.handlers.shell.Handler._get_environment')
    @mock.patch('solum.objects.registry')
    @mock.patch('solum.conductor.api.API.build_job_update')
    @mock.patch('subprocess.Popen')
    def test_build_fail(self, mock_popen, mock_b_update, mock_registry,
                        mock_get_env):
        handler = shell_handler.Handler()
        fake_assembly = fakes.FakeAssembly()
        mock_registry.Assembly.get_by_id.return_value = fake_assembly
        mock_popen.return_value.communicate.return_value = [
            'foo\ncreated_image_id= \n', None]
        test_env = mock_environment()
        mock_get_env.return_value = test_env
        git_info = mock_git_info()
        handler.build(self.ctx, build_id=5, git_info=git_info, name='new_app',
                      base_image_id='1-2-3-4', source_format='heroku',
                      image_format='docker', assembly_id=44, test_cmd=None)

        proj_dir = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                '..', '..', '..', '..'))
        script = os.path.join(proj_dir, 'contrib/lp-cedarish/docker/build-app')
        mock_popen.assert_called_once_with([script, 'git://example.com/foo',
                                            'new_app', self.ctx.tenant,
                                            '1-2-3-4'],
                                           env=test_env, stdout=-1)
        expected = [mock.call(5, 'BUILDING', 'Starting the image build',
                              None, 44),
                    mock.call(5, 'ERROR', 'image not created', None, 44)]

        self.assertEqual(expected, mock_b_update.call_args_list)

    @mock.patch('solum.worker.handlers.shell.Handler._get_environment')
    @mock.patch('solum.objects.registry')
    @mock.patch('subprocess.Popen')
    @mock.patch('solum.worker.handlers.shell.update_assembly_status')
    def test_unittest(self, mock_a_update, mock_popen, mock_registry,
                      mock_get_env):
        handler = shell_handler.Handler()
        fake_assembly = fakes.FakeAssembly()
        mock_registry.Assembly.get_by_id.return_value = fake_assembly
        test_env = mock_environment()
        mock_get_env.return_value = test_env
        mock_popen.return_value.wait.return_value = 0
        git_info = mock_git_info()
        handler.unittest(self.ctx, assembly_id=fake_assembly.id,
                         git_info=git_info, test_cmd='tox')

        proj_dir = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                '..', '..', '..', '..'))
        script = os.path.join(proj_dir,
                              'contrib/lp-cedarish/docker/unittest-app')
        mock_popen.assert_called_once_with([script, 'git://example.com/foo',
                                            'master', self.ctx.tenant, 'tox'],
                                           env=test_env, stdout=-1)
        expected = [mock.call(self.ctx, 8, 'UNIT_TESTING')]

        self.assertEqual(expected, mock_a_update.call_args_list)

    @mock.patch('solum.worker.handlers.shell.Handler._get_environment')
    @mock.patch('solum.objects.registry')
    @mock.patch('subprocess.Popen')
    @mock.patch('solum.worker.handlers.shell.update_assembly_status')
    def test_unittest_failure(self, mock_a_update, mock_popen, mock_registry,
                              mock_get_env):
        handler = shell_handler.Handler()
        fake_assembly = fakes.FakeAssembly()
        mock_registry.Assembly.get_by_id.return_value = fake_assembly
        test_env = mock_environment()
        mock_get_env.return_value = test_env
        mock_popen.return_value.wait.return_value = 1
        git_info = mock_git_info()
        handler.unittest(self.ctx, assembly_id=fake_assembly.id,
                         git_info=git_info, test_cmd='tox')

        proj_dir = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                '..', '..', '..', '..'))
        script = os.path.join(proj_dir,
                              'contrib/lp-cedarish/docker/unittest-app')
        mock_popen.assert_called_once_with([script, 'git://example.com/foo',
                                            'master', self.ctx.tenant, 'tox'],
                                           env=test_env, stdout=-1)
        expected = [mock.call(self.ctx, 8, 'UNIT_TESTING'),
                    mock.call(self.ctx, 8, 'UNIT_TESTING_FAILED')]

        self.assertEqual(expected, mock_a_update.call_args_list)

    @mock.patch('solum.worker.handlers.shell.Handler._get_environment')
    @mock.patch('solum.objects.registry')
    @mock.patch('subprocess.Popen')
    @mock.patch('solum.conductor.api.API.build_job_update')
    @mock.patch('solum.worker.handlers.shell.update_assembly_status')
    @mock.patch('solum.deployer.api.API.deploy')
    def test_unittest_and_build(self, mock_deploy, mock_a_update,
                                mock_b_update, mock_popen, mock_registry,
                                mock_get_env):

        handler = shell_handler.Handler()
        fake_assembly = fakes.FakeAssembly()
        fake_glance_id = str(uuid.uuid4())
        mock_registry.Assembly.get_by_id.return_value = fake_assembly
        mock_popen.return_value.wait.return_value = 0
        mock_popen.return_value.communicate.return_value = [
            'foo\ncreated_image_id=%s' % fake_glance_id, None]
        test_env = mock_environment()
        mock_get_env.return_value = test_env
        git_info = mock_git_info()
        handler.build(self.ctx, build_id=5, git_info=git_info, name='new_app',
                      base_image_id='1-2-3-4', source_format='heroku',
                      image_format='docker', assembly_id=44,
                      test_cmd='faketests')

        proj_dir = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                '..', '..', '..', '..'))
        util_dir = os.path.join(proj_dir, 'contrib', 'lp-cedarish', 'docker')
        u_script = os.path.join(util_dir, 'unittest-app')
        b_script = os.path.join(util_dir, 'build-app')

        expected = [
            mock.call([u_script, 'git://example.com/foo', 'master',
                       self.ctx.tenant, 'faketests'], env=test_env, stdout=-1),
            mock.call([b_script, 'git://example.com/foo', 'new_app',
                       self.ctx.tenant, '1-2-3-4'], env=test_env, stdout=-1)]
        self.assertEqual(expected, mock_popen.call_args_list)

        expected = [mock.call(5, 'BUILDING', 'Starting the image build',
                              None, 44),
                    mock.call(5, 'COMPLETE', 'built successfully',
                              fake_glance_id, 44)]
        self.assertEqual(expected, mock_b_update.call_args_list)

        expected = [mock.call(self.ctx, 44, 'UNIT_TESTING'),
                    mock.call(self.ctx, 44, 'BUILDING')]
        self.assertEqual(expected, mock_a_update.call_args_list)

        expected = [mock.call(assembly_id=44, image_id=fake_glance_id)]
        self.assertEqual(expected, mock_deploy.call_args_list)

    @mock.patch('solum.worker.handlers.shell.Handler._get_environment')
    @mock.patch('subprocess.Popen')
    @mock.patch('solum.worker.handlers.shell.update_assembly_status')
    def test_unittest_no_build(self, mock_a_update, mock_popen, mock_get_env):
        handler = shell_handler.Handler()
        mock_popen.return_value.wait.return_value = 1
        test_env = mock_environment()
        mock_get_env.return_value = test_env
        git_info = mock_git_info()
        handler.build(self.ctx, build_id=5, git_info=git_info, name='new_app',
                      base_image_id='1-2-3-4', source_format='heroku',
                      image_format='docker', assembly_id=44,
                      test_cmd='faketests')

        proj_dir = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                '..', '..', '..', '..'))
        util_dir = os.path.join(proj_dir, 'contrib', 'lp-cedarish', 'docker')
        u_script = os.path.join(util_dir, 'unittest-app')

        expected = [
            mock.call([u_script, 'git://example.com/foo', 'master',
                       self.ctx.tenant, 'faketests'], env=test_env, stdout=-1)]
        self.assertEqual(expected, mock_popen.call_args_list)

        expected = [mock.call(self.ctx, 44, 'UNIT_TESTING'),
                    mock.call(self.ctx, 44, 'UNIT_TESTING_FAILED')]
        self.assertEqual(expected, mock_a_update.call_args_list)


class TestNotifications(base.BaseTestCase):
    def setUp(self):
        super(TestNotifications, self).setUp()
        self.ctx = utils.dummy_context()
        self.db = self.useFixture(utils.Database())

    @mock.patch('solum.objects.registry')
    def test_update_assembly_status(self, mock_registry):
        mock_assembly = mock.MagicMock()
        mock_registry.Assembly.get_by_id.return_value = mock_assembly
        shell_handler.update_assembly_status(self.ctx, '1234',
                                             'BUILDING')
        mock_registry.Assembly.get_by_id.assert_called_once_with(self.ctx,
                                                                 '1234')
        mock_assembly.save.assert_called_once_with(self.ctx)
        self.assertEqual(mock_assembly.status, 'BUILDING')

    @mock.patch('solum.objects.registry')
    def test_update_assembly_status_pass(self, mock_registry):
        shell_handler.update_assembly_status(self.ctx, None,
                                             'BUILDING')
        self.assertEqual(mock_registry.call_count, 0)


class TestBuildCommand(base.BaseTestCase):
    scenarios = [
        ('docker',
         dict(source_format='heroku', image_format='docker',
              base_image_id='auto',
              expect='lp-cedarish/docker/build-app')),
        ('vmslug',
         dict(source_format='heroku', image_format='qcow2',
              base_image_id='auto',
              expect='lp-cedarish/vm-slug/build-app')),
        ('dockerfile',
         dict(source_format='dockerfile', image_format='docker',
              base_image_id='auto',
              expect='lp-dockerfile/docker/build-app')),
        ('dib',
         dict(source_format='dib', image_format='qcow2',
              base_image_id='xyz',
              expect='diskimage-builder/vm-slug/build-app'))]

    def test_build_cmd(self):
        ctx = utils.dummy_context()
        handler = shell_handler.Handler()
        cmd = handler._get_build_command(ctx,
                                         'http://example.com/a.git',
                                         'testa',
                                         self.base_image_id,
                                         self.source_format,
                                         self.image_format)
        self.assertIn(self.expect, cmd[0])
        self.assertEqual('http://example.com/a.git', cmd[1])
        self.assertEqual('testa', cmd[2])
        self.assertEqual(ctx.tenant, cmd[3])
        if self.base_image_id == 'auto' and self.image_format == 'qcow2':
            self.assertEqual('cedarish', cmd[4])
        else:
            self.assertEqual(self.base_image_id, cmd[4])
