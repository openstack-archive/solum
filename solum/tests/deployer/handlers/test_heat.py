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
from oslo.config import cfg

from solum.deployer.handlers import heat as heat_handler
from solum.objects import assembly
from solum.tests import base
from solum.tests import fakes
from solum.tests import utils


STATES = assembly.States


class HandlerTest(base.BaseTestCase):
    def setUp(self):
        super(HandlerTest, self).setUp()
        self.ctx = utils.dummy_context()

    def test_create(self):
        handler = heat_handler.Handler()
        handler.echo = mock.MagicMock()
        handler.echo({}, 'foo')
        handler.echo.assert_called_once_with({}, 'foo')

    @mock.patch('solum.common.catalog.get')
    @mock.patch('solum.objects.registry')
    @mock.patch('solum.common.clients.OpenStackClients')
    def test_deploy(self, mock_clients, mock_registry, mock_get_templ):
        handler = heat_handler.Handler()

        fake_assembly = fakes.FakeAssembly()
        mock_registry.Assembly.get_by_id.return_value = fake_assembly
        fake_template = json.dumps({'description': 'test'})
        mock_get_templ.return_value = fake_template
        handler._find_id_if_stack_exists = mock.MagicMock(return_value=(None))
        stacks = mock_clients.return_value.heat.return_value.stacks
        stacks.create.return_value = {"stack": {
            "id": "fake_id",
            "links": [{"href": "http://fake.ref",
                       "rel": "self"}]}}
        neutron = mock_clients.return_value.neutron
        neutron.return_value.list_networks.return_value = {
            "networks": [{"router:external": True,
                          "id": "public_net_id"},
                         {"router:external": False,
                          "id": "private_net_id",
                          "subnets": ["private_subnet_id"]}]}
        handler._update_assembly_status = mock.MagicMock()
        handler.deploy(self.ctx, 77, 'created_image_id')
        parameters = {'image': 'created_image_id',
                      'app_name': 'faker',
                      'private_net': 'private_net_id',
                      'public_net': 'public_net_id',
                      'private_subnet': 'private_subnet_id'}
        stacks = mock_clients.return_value.heat.return_value.stacks
        stacks.create.assert_called_once_with(stack_name='faker-test_uuid',
                                              template=fake_template,
                                              parameters=parameters)
        neutron = mock_clients.return_value.neutron
        neutron.return_value.list_networks.assert_called_once_with()
        assign_and_create_mock = mock_registry.Component.assign_and_create
        assign_and_create_mock.assert_called_once_with(self.ctx,
                                                       fake_assembly,
                                                       'Heat Stack',
                                                       'Heat Stack test',
                                                       'http://fake.ref')

    @mock.patch('solum.common.catalog.get')
    @mock.patch('solum.objects.registry')
    @mock.patch('solum.common.clients.OpenStackClients')
    @mock.patch('solum.deployer.handlers.heat.cfg.CONF.api.image_format')
    def test_deploy_docker(self, image_format, mock_clients, mock_registry,
                           mock_get_templ):
        handler = heat_handler.Handler()
        image_format.return_value = "docker"
        fake_assembly = fakes.FakeAssembly()
        mock_registry.Assembly.get_by_id.return_value = fake_assembly
        fake_template = json.dumps({'description': 'test'})
        mock_get_templ.return_value = fake_template
        handler._find_id_if_stack_exists = mock.MagicMock(return_value=(None))
        stacks = mock_clients.return_value.heat.return_value.stacks
        stacks.create.return_value = {"stack": {
            "id": "fake_id",
            "links": [{"href": "http://fake.ref",
                       "rel": "self"}]}}
        handler._update_assembly_status = mock.MagicMock()
        handler.deploy(self.ctx, 77, 'created_image_id')
        parameters = {'image': 'created_image_id',
                      'app_name': 'faker'}
        stacks.create.assert_called_once_with(stack_name='faker-test_uuid',
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
        handler = heat_handler.Handler()
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
        handler = heat_handler.Handler()
        fake_assembly = fakes.FakeAssembly()
        stack = mock.MagicMock()
        stack.status = 'FAILED'
        mock_clients.heat().stacks.get.return_value = stack
        handler._update_assembly_status(self.ctx, fake_assembly, mock_clients,
                                        'fake_id')
        self.assertEqual(fake_assembly.status, 'ERROR')
        fake_assembly.save.assert_called_once_with(self.ctx)

    def test_parse_server_url(self):
        handler = heat_handler.Handler()
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

    @mock.patch('solum.common.clients.OpenStackClients')
    def test_find_id_if_stack_exists(self, mock_clients):
        handler = heat_handler.Handler()
        stack = mock.MagicMock
        stack.identifier = 'test/123'
        mock_clients.heat.stacks.get.return_value = stack
        id = handler._find_id_if_stack_exists(mock_clients, 'test')
        self.assertEqual(id, '123')

    @mock.patch('solum.objects.registry')
    @mock.patch('solum.common.clients.OpenStackClients')
    def test_delete_heat_stack_success(self, mock_client, mock_registry):
        fake_assem = fakes.FakeAssembly()
        mock_registry.Assembly.get_by_id.return_value = fake_assem

        handler = heat_handler.Handler()
        handler._find_id_if_stack_exists = mock.MagicMock(
            side_effect=self._s_efct)

        cfg.CONF.deployer.max_attempts = 1
        cfg.CONF.deployer.wait_interval = 0
        cfg.CONF.deployer.growth_factor = 1.2

        handler.delete_heat_stack(self.ctx, fake_assem.id)

        mock_client.heat.stacks.delete.assert_called_once()
        fake_assem.destroy.assert_called_once()

    def _s_efct(*args):
        def second_call(*args):
            return None
        return mock.MagicMock(side_effect=second_call)

    @mock.patch('solum.objects.registry')
    @mock.patch('solum.common.clients.OpenStackClients')
    def test_delete_heat_stack_error(self, mock_client, mock_registry):
        fake_assem = fakes.FakeAssembly()
        mock_registry.Assembly.get_by_id.return_value = fake_assem

        handler = heat_handler.Handler()
        handler._find_id_if_stack_exists = mock.MagicMock(return_value='42')

        cfg.CONF.deployer.max_attempts = 1
        cfg.CONF.deployer.wait_interval = 0
        cfg.CONF.deployer.growth_factor = 1.2

        handler.delete_heat_stack(self.ctx, fake_assem.id)

        mock_client.heat.stacks.delete.assert_called_once()
        fake_assem.save.assert_called_once_with(self.ctx)
        self.assertEqual(STATES.ERROR_STACK_DELETE_FAILED, fake_assem.status)

    @mock.patch('solum.objects.registry')
    @mock.patch('solum.common.clients.OpenStackClients')
    def test_delete_heat_stack_absent(self, mock_client, mock_registry):
        fake_assem = fakes.FakeAssembly()
        mock_registry.Assembly.get_by_id.return_value = fake_assem

        handler = heat_handler.Handler()
        handler._find_id_if_stack_exists = mock.MagicMock(return_value=None)
        handler.delete_heat_stack(self.ctx, fake_assem.id)

        assert not mock_client.heat.stacks.delete.called
        fake_assem.destroy.assert_called_once()
