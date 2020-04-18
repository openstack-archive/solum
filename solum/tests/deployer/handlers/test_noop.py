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

from unittest import mock

from solum.deployer.handlers import noop as noop_handler
from solum.i18n import _
from solum.tests import base
from solum.tests import fakes
from solum.tests import utils


class HandlerTest(base.BaseTestCase):
    def setUp(self):
        super(HandlerTest, self).setUp()
        self.ctx = utils.dummy_context()

    @mock.patch('solum.deployer.handlers.noop.LOG')
    def test_echo(self, fake_LOG):
        noop_handler.Handler().echo({}, 'foo')
        fake_LOG.debug.assert_called_once_with(_('%s') % 'foo')

    @mock.patch('solum.deployer.handlers.noop.LOG')
    def test_deploy(self, fake_LOG):
        args = [77, 'created_image_id', [80]]
        noop_handler.Handler().deploy(self.ctx, *args)
        message = 'Deploy %s %s %s' % tuple(args)
        fake_LOG.debug.assert_called_once_with(_("%s") % message)

    @mock.patch('solum.objects.registry')
    @mock.patch('solum.deployer.handlers.noop.LOG')
    def test_destroy(self, fake_LOG, fake_registry):
        fake_assembly = fakes.FakeAssembly()
        fake_registry.Assembly.get_by_id.return_value = fake_assembly
        args = [fake_assembly.id]
        noop_handler.Handler().destroy_assembly(self.ctx, *args)
        fake_assembly.destroy.assert_called_once_with(self.ctx)

        message = 'Destroy %s' % tuple(args)
        fake_LOG.debug.assert_called_once_with(_("%s") % message)
