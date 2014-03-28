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
import mock

from solum.deployer.handlers import default
from solum.tests import base
from solum.tests import fakes
from solum.tests import utils


class HandlerTest(base.BaseTestCase):
    def setUp(self):
        super(HandlerTest, self).setUp()
        self.ctx = utils.dummy_context()

    def test_create(self):
        handler = default.Handler()
        handler.echo = mock.MagicMock()
        handler.echo({}, 'foo')
        handler.echo.assert_called_once_with({}, 'foo')

    @mock.patch('solum.deployer.handlers.default.Handler._get_template')
    @mock.patch('solum.objects.registry')
    @mock.patch('solum.common.clients.OpenStackClients')
    def test_deploy(self, mock_clients, mock_registry, mock_get_templ):
        handler = default.Handler()

        mock_registry.Assembly.get_by_id.return_value = \
            fakes.FakeAssembly()
        fake_template = json.dumps({'description': 'test'})
        mock_get_templ.return_value = fake_template
        mock_clients.return_value.heat.return_value.stacks.create.\
            return_value = {'stack_id': 'stack2'}

        handler.deploy(self.ctx, 77, 'created_image_id')
        parameters = {'image': 'created_image_id',
                      'app_name': 'faker'}
        mock_clients.return_value.heat.return_value.stacks.create.\
            assert_called_once_with(stack_name='faker',
                                    template=fake_template,
                                    parameters=parameters)

        mock_clients.return_value.heat.return_value.stacks.get.\
            assert_called_once_with(stack_id='stack2')
