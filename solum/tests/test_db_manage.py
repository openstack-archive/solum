#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import sys
from unittest import mock


from solum.cmd import db_manage as cli
from solum.tests import base


class TestCli(base.BaseTestCase):
    scenarios = [
        ('stamp', dict(
            argv=['prog', 'stamp', 'foo'],
            func_name='stamp',
            exp_args=('foo',), exp_kwargs={})),
        ('version', dict(
            argv=['prog', 'version'],
            func_name='version',
            exp_args=[], exp_kwargs={})),
        ('revision_auto', dict(
            argv=['prog', 'revision', '--autogenerate', '-m' 'message'],
            func_name='revision', exp_args=[],
            exp_kwargs={'message': 'message',
                        'autogenerate': True})),
        ('revision', dict(
            argv=['prog', 'revision', '-m', 'message'],
            func_name='revision', exp_args=[],
            exp_kwargs={'message': 'message',
                        'autogenerate': False})),
        ('upgrade', dict(
            argv=['prog', 'upgrade', 'head'],
            func_name='upgrade', exp_args=('head',),
            exp_kwargs={})),
        ('downgrade', dict(
            argv=['prog', 'downgrade', 'folsom'],
            func_name='downgrade', exp_args=('folsom',),
            exp_kwargs={})),
    ]

    def setUp(self):
        super(TestCli, self).setUp()
        self.addCleanup(cli.CONF.reset)

    @mock.patch.object(cli, 'get_manager')
    def test_alembic_manager(self, mock_get_manager):
        manager = mock_get_manager.return_value
        with mock.patch.object(sys, 'argv', self.argv):
            cli.main()
            mock_get_manager.assert_called_once_with()
            test_method = getattr(manager, self.func_name)
            test_method.assert_called_once_with(*self.exp_args,
                                                **self.exp_kwargs)
