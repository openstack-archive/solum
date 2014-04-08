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

import mock

from solum.deployer.handlers import default as default_handler
from solum.openstack.common.gettextutils import _
from solum.tests import base
from solum.tests import utils


class HandlerTest(base.BaseTestCase):
    def setUp(self):
        super(HandlerTest, self).setUp()
        self.ctx = utils.dummy_context()

    @mock.patch('solum.deployer.handlers.default.LOG')
    def test_echo(self, fake_LOG):
        default_handler.Handler().echo({}, 'foo')
        fake_LOG.debug.assert_called_once_with(_('%s') % 'foo')

    @mock.patch('solum.deployer.handlers.default.LOG')
    def test_deploy(self, fake_LOG):
        args = [5, 'git://example.com/foo', 'new_app',
                '1-2-3-4', 'heroku', 'docker', 44]
        args = [77, 'created_image_id']
        default_handler.Handler().deploy(self.ctx, *args)
        message = 'Deploy %s %s' % tuple(args)
        fake_LOG.debug.assert_called_once_with(_("%s") % message)
