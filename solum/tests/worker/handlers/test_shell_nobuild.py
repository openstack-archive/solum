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

import os.path
import uuid

import mock
from oslo.config import cfg

from solum.tests import base
from solum.tests import fakes
from solum.tests import utils
from solum.tests.worker.handlers import test_shell
from solum.worker.handlers import shell_nobuild as shell_handler


class HandlerTest(base.BaseTestCase):
    def setUp(self):
        super(HandlerTest, self).setUp()
        self.ctx = utils.dummy_context()

    # Notice most of these mocks do not modify shell_nobuild, but shell.
    @mock.patch('solum.worker.handlers.shell.Handler._get_environment')
    @mock.patch('httplib2.Http.request')
    @mock.patch('solum.objects.registry')
    @mock.patch('subprocess.Popen')
    @mock.patch('solum.conductor.api.API.build_job_update')
    @mock.patch('solum.worker.handlers.shell.update_assembly_status')
    @mock.patch('solum.worker.handlers.shell_nobuild.update_assembly_status')
    def test_unittest_and_build(self, mock_a_update_nb, mock_a_update,
                                mock_b_update, mock_popen, mock_registry,
                                mock_req, mock_get_env):
        handler = shell_handler.Handler()
        fake_assembly = fakes.FakeAssembly()
        fake_glance_id = str(uuid.uuid4())
        mock_registry.Assembly.get_by_id.return_value = fake_assembly
        mock_popen.return_value.wait.return_value = 0
        mock_popen.return_value.communicate.return_value = [
            'foo\ncreated_image_id=%s' % fake_glance_id, None]
        test_env = test_shell.mock_environment()
        mock_get_env.return_value = test_env
        git_info = test_shell.mock_git_info()
        status_token = git_info.get('status_token')
        status_url = git_info.get('status_url')
        mock_req.return_value = test_shell.mock_http_response()
        cfg.CONF.worker.log_url_prefix = "https://log.com/commit/"

        handler.build(self.ctx, build_id=5, git_info=git_info, name='new_app',
                      base_image_id='1-2-3-4', source_format='heroku',
                      image_format='docker', assembly_id=44,
                      test_cmd='faketests', source_creds_ref=None)

        expected = [
            mock.call(status_url, 'POST',
                      headers=test_shell.mock_request_hdr(status_token),
                      body=test_shell.mock_req_pending_body(
                          'https://log.com/commit/SHA')),
            mock.call(status_url, 'POST',
                      headers=test_shell.mock_request_hdr(status_token),
                      body=test_shell.mock_req_success_body(
                          'https://log.com/commit/SHA'))]

        self.assertEqual(expected, mock_req.call_args_list)

        proj_dir = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                '..', '..', '..', '..'))
        util_dir = os.path.join(proj_dir, 'contrib', 'lp-cedarish', 'docker')
        u_script = os.path.join(util_dir, 'unittest-app')

        expected = [
            mock.call([u_script, 'git://example.com/foo', 'master',
                       self.ctx.tenant, '', 'faketests'], env=test_env,
                      stdout=-1)]
        self.assertEqual(expected, mock_popen.call_args_list)

        # The UNIT_TESTING update happens from shell...
        expected = [mock.call(self.ctx, 44, 'UNIT_TESTING')]
        self.assertEqual(expected, mock_a_update.call_args_list)

        # ...but the READY update happens in shell_nobuild.
        expected = [mock.call(self.ctx, 44, 'READY')]
        self.assertEqual(expected, mock_a_update_nb.call_args_list)

    @mock.patch('solum.worker.handlers.shell.Handler._get_environment')
    @mock.patch('httplib2.Http.request')
    @mock.patch('subprocess.Popen')
    @mock.patch('solum.worker.handlers.shell.update_assembly_status')
    @mock.patch('solum.objects.registry')
    def test_unittest_no_build(self, mock_registry, mock_a_update,
                               mock_popen, mock_req, mock_get_env):
        handler = shell_handler.Handler()
        fake_assembly = fakes.FakeAssembly()
        mock_registry.Assembly.get_by_id.return_value = fake_assembly
        mock_popen.return_value.wait.return_value = 1
        test_env = test_shell.mock_environment()
        mock_get_env.return_value = test_env
        git_info = test_shell.mock_git_info()
        status_token = git_info.get('status_token')
        status_url = git_info.get('status_url')
        mock_req.return_value = test_shell.mock_http_response()
        cfg.CONF.worker.log_url_prefix = "https://log.com/commit/"

        handler.build(self.ctx, build_id=5, git_info=git_info,
                      name='new_app', base_image_id='1-2-3-4',
                      source_format='heroku', image_format='docker',
                      assembly_id=44, test_cmd='faketests',
                      source_creds_ref=None)

        expected = [
            mock.call(status_url, 'POST',
                      headers=test_shell.mock_request_hdr(status_token),
                      body=test_shell.mock_req_pending_body(
                          'https://log.com/commit/SHA')),
            mock.call(status_url, 'POST',
                      headers=test_shell.mock_request_hdr(status_token),
                      body=test_shell.mock_req_failure_body(
                          'https://log.com/commit/SHA'))]
        self.assertEqual(expected, mock_req.call_args_list)

        proj_dir = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                '..', '..', '..', '..'))
        util_dir = os.path.join(proj_dir, 'contrib', 'lp-cedarish', 'docker')
        u_script = os.path.join(util_dir, 'unittest-app')

        expected = [
            mock.call([u_script, 'git://example.com/foo', 'master',
                       self.ctx.tenant, '', 'faketests'], env=test_env,
                      stdout=-1)]
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
