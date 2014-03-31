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

        fake_assembly = fakes.FakeAssembly()
        mock_registry.Assembly.get_by_id.return_value = fake_assembly
        fake_template = json.dumps({'description': 'test'})
        mock_get_templ.return_value = fake_template
        mock_clients.return_value.heat.return_value.stacks.create.\
            return_value = {"stack": {"id": "fake_id",
                                      "links": [{"href": "http://fake.ref",
                                                 "rel": "self"}]}}
        handler._update_assembly_status = mock.MagicMock()
        handler.deploy(self.ctx, 77, 'created_image_id')
        parameters = {'image': 'created_image_id',
                      'app_name': 'faker'}
        mock_clients.return_value.heat.return_value.stacks.create.\
            assert_called_once_with(stack_name='faker',
                                    template=fake_template,
                                    parameters=parameters)
        assign_and_create_mock = mock_registry.Component.assign_and_create
        assign_and_create_mock.assert_called_once_with(self.ctx,
                                                       fake_assembly,
                                                       'Heat Stack',
                                                       'Heat Stack test',
                                                       'http://fake.ref')

    @mock.patch('solum.common.clients.OpenStackClients')
    def test_update_assembly_status(self, mock_clients):
        handler = default.Handler()
        fake_assembly = fakes.FakeAssembly()
        stack = mock.MagicMock()
        stack.status = 'COMPLETE'
        mock_clients.heat().stacks.get.return_value = stack
        handler._parse_server_url = mock.MagicMock(return_value=('xyz'))
        handler._update_assembly_status(self.ctx, fake_assembly, mock_clients,
                                        'fake_id')
        self.assertEqual(fake_assembly.status, 'READY')
        fake_assembly.save.assert_called_once_with(self.ctx)

    @mock.patch('solum.common.clients.OpenStackClients')
    def test_update_assembly_status_failed(self, mock_clients):
        handler = default.Handler()
        fake_assembly = fakes.FakeAssembly()
        stack = mock.MagicMock()
        stack.status = 'FAILED'
        mock_clients.heat().stacks.get.return_value = stack
        handler._update_assembly_status(self.ctx, fake_assembly, mock_clients,
                                        'fake_id')
        self.assertEqual(fake_assembly.status, 'ERROR')
        fake_assembly.save.assert_called_once_with(self.ctx)

    def test_parse_server_url(self):
        handler = default.Handler()
        heat_output = mock.MagicMock()
        heat_output._info = {"id": "fake_id",
                             "outputs": [{"output_value": "192.168.78.21",
                                          "description": "IP", "output_key":
                                          "public_ip"},
                                         {"output_value":
                                          "http://192.168.78.21:5000",
                                          "description": "URL", "output_key":
                                          "URL"}]}
        host_url = handler._parse_server_url(heat_output)
        self.assertEqual(host_url, "http://192.168.78.21:5000")
