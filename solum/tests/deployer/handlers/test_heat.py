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
from unittest import mock

from heatclient import exc
from oslo_config import cfg
import yaml

from solum.common import exception
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

    @mock.patch('solum.deployer.handlers.heat.tlog')
    @mock.patch('solum.deployer.handlers.heat.update_assembly')
    @mock.patch('solum.common.catalog.get')
    @mock.patch('solum.objects.registry')
    @mock.patch('solum.common.clients.OpenStackClients')
    @mock.patch('solum.deployer.handlers.heat.get_app_by_assem_id')
    @mock.patch('solum.deployer.handlers.heat.get_heat_client')
    def test_deploy_docker_on_vm_with_dreg(self, mock_ht_cl,
                                           mock_get_app, mock_clients,
                                           mock_registry, mock_get_templ,
                                           mock_ua, m_log):
        handler = heat_handler.Handler()

        fake_assembly = fakes.FakeAssembly()

        m_log.TenantLogger.call.return_value = mock.MagicMock()

        mock_registry.Assembly.get_by_id.return_value = fake_assembly
        fake_template = self._get_fake_template()
        template = self._get_tmpl_for_docker_reg(fake_assembly, fake_template,
                                                 'created_image_id')
        cfg.CONF.api.image_format = "vm"
        cfg.CONF.worker.image_storage = "docker_registry"
        mock_get_templ.return_value = template
        handler._find_id_if_stack_exists = mock.MagicMock(return_value=(None))

        created_stack = {"stack": {
            "id": "fake_id",
            "links": [{"href": "http://fake.ref",
                       "rel": "self"}]}}

        mock_ht_cl.return_value.stacks.create.return_value = created_stack
        handler._check_stack_status = mock.MagicMock()

        handler.deploy(self.ctx, 77, 'created_image_id', 'image_name', [80])
        self.assertTrue(mock_ht_cl.return_value.stacks.create.called)
        assign_and_create_mock = mock_registry.Component.assign_and_create
        comp_name = 'Heat_Stack_for_%s' % fake_assembly.name
        assign_and_create_mock.assert_called_once_with(self.ctx,
                                                       fake_assembly,
                                                       comp_name,
                                                       'heat_stack',
                                                       'Heat Stack test',
                                                       'http://fake.ref',
                                                       'fake_id')

    @mock.patch('solum.deployer.handlers.heat.tlog')
    @mock.patch('solum.deployer.handlers.heat.update_assembly')
    @mock.patch('solum.common.catalog.get')
    @mock.patch('solum.common.catalog.get_from_contrib')
    @mock.patch('solum.objects.registry')
    @mock.patch('solum.common.clients.OpenStackClients')
    @mock.patch('solum.deployer.handlers.heat.get_heat_client')
    def test_deploy_docker_on_vm_swift(self, heat_clnt, mock_clients,
                                       mock_registry,
                                       mock_contrib, mock_get_templ,
                                       mock_ua, m_log):
        handler = heat_handler.Handler()

        mock_log = m_log.TenantLogger.return_value.log
        fake_assembly = fakes.FakeAssembly()
        mock_registry.Assembly.get_by_id.return_value = fake_assembly
        fake_template = self._get_fake_template()
        img = "http://a.b.c/d?temp_url_sig=v&temp_url_expires=v"

        mock_contrib.return_value = "robust_file"
        get_file_dict = {}
        get_file_dict[self._get_key()] = "robust_file"

        cfg.CONF.api.image_format = "vm"
        cfg.CONF.worker.image_storage = "swift"
        cfg.CONF.deployer.flavor = "flavor"
        cfg.CONF.deployer.image = "coreos"
        mock_get_templ.return_value = fake_template
        handler._find_id_if_stack_exists = mock.MagicMock(return_value=(None))

        created_stack = {"stack": {
            "id": "fake_id",
            "links": [{"href": "http://fake.ref",
                       "rel": "self"}]}}
        heat_clnt.return_value.stacks.create.return_value = created_stack

        handler._check_stack_status = mock.MagicMock()

        handler.deploy(self.ctx, 77, img, 'tenant-name-ts-commit', [80])

        parameters = {'name': fake_assembly.uuid,
                      'flavor': "flavor",
                      'image': "coreos",
                      'key_name': "mykey",
                      'location': img,
                      'du': 'tenant-name-ts-commit',
                      'publish_ports': '-p 80:80'}

        heat_clnt.return_value.stacks.create.assert_called_once_with(
            stack_name='faker-test_uuid',
            template=fake_template,
            parameters=parameters,
            files=get_file_dict)
        assign_and_create_mock = mock_registry.Component.assign_and_create
        comp_name = 'Heat_Stack_for_%s' % fake_assembly.name
        assign_and_create_mock.assert_called_once_with(self.ctx,
                                                       fake_assembly,
                                                       comp_name,
                                                       'heat_stack',
                                                       'Heat Stack test',
                                                       'http://fake.ref',
                                                       'fake_id')
        self.assertTrue(mock_log.called)

    @mock.patch('solum.deployer.handlers.heat.tlog')
    @mock.patch('solum.deployer.handlers.heat.update_assembly')
    @mock.patch('solum.common.catalog.get')
    @mock.patch('solum.objects.registry')
    @mock.patch('solum.common.clients.OpenStackClients')
    @mock.patch('solum.deployer.handlers.heat.get_heat_client')
    def test_comp_name_error(self, heat_clnt, mock_clients, mock_registry,
                             mock_get_templ, mock_ua, m_log):
        handler = heat_handler.Handler()

        mock_log = m_log.TenantLogger.return_value.log

        fake_assembly = fakes.FakeAssembly()
        mock_registry.Assembly.get_by_id.return_value = fake_assembly
        fake_template = json.dumps({'description': 'test'})
        mock_get_templ.return_value = fake_template
        handler._find_id_if_stack_exists = mock.MagicMock(return_value=(None))
        stacks = heat_clnt.return_value.heat.return_value.stacks
        stacks.create.return_value = {"stack": {
            "id": "fake_id",
            "links": [{"href": "http://fake.ref",
                       "rel": "self"}]}}
        handler._check_stack_status = mock.MagicMock()
        handler.deploy(self.ctx, 77, 'created_image_id', 'image_name', [80])
        assign_and_create_mock = mock_registry.Component.assign_and_create
        comp_name = 'Heat Stack for %s' % fake_assembly.name
        self.assertRaises(AssertionError,
                          assign_and_create_mock.assert_called_once_with,
                          comp_name)
        self.assertTrue(mock_log.called)

    @mock.patch('solum.deployer.handlers.heat.tlog')
    @mock.patch('solum.deployer.handlers.heat.update_assembly')
    @mock.patch('solum.common.catalog.get')
    @mock.patch('solum.common.catalog.get_from_contrib')
    @mock.patch('solum.objects.registry')
    @mock.patch('solum.common.clients.OpenStackClients')
    @mock.patch('solum.deployer.handlers.heat.get_heat_client')
    def test_deploy_docker(self, heat_clnt, mock_clients, mock_registry,
                           mock_get_contrib, mock_get_templ, mock_ua, m_log):
        handler = heat_handler.Handler()
        fake_assembly = fakes.FakeAssembly()
        mock_registry.Assembly.get_by_id.return_value = fake_assembly

        m_log.TenantLogger.call.return_value = mock.MagicMock()

        cfg.CONF.api.image_format = "docker"

        mock_get_contrib.return_value = "robust_file"
        get_file_dict = {}
        get_file_dict[self._get_key()] = "robust_file"

        fake_template = self._get_fake_template()
        template = self._get_tmpl_for_docker_reg(fake_assembly, fake_template,
                                                 'created_image_id')
        mock_get_templ.return_value = template

        handler._find_id_if_stack_exists = mock.MagicMock(return_value=(None))
        created_stack = {"stack": {
            "id": "fake_id",
            "links": [{"href": "http://fake.ref",
                       "rel": "self"}]}}
        heat_clnt.return_value.stacks.create.return_value = created_stack
        handler._check_stack_status = mock.MagicMock()

        handler.deploy(self.ctx, 77, 'created_image_id', 'image_name', [80])

        parameters = {'image': 'created_image_id',
                      'app_name': 'faker',
                      'port': 80}

        heat_clnt.return_value.stacks.create.assert_called_once_with(
            stack_name='faker-test_uuid',
            template=template,
            parameters=parameters,
            files=get_file_dict)
        assign_and_create_mock = mock_registry.Component.assign_and_create
        comp_name = 'Heat_Stack_for_%s' % fake_assembly.name
        assign_and_create_mock.assert_called_once_with(self.ctx,
                                                       fake_assembly,
                                                       comp_name,
                                                       'heat_stack',
                                                       'Heat Stack test',
                                                       'http://fake.ref',
                                                       'fake_id')

    @mock.patch('solum.deployer.handlers.heat.update_wf_and_app')
    @mock.patch('solum.deployer.handlers.heat.update_assembly')
    @mock.patch('solum.common.clients.OpenStackClients')
    @mock.patch('httplib2.Http')
    @mock.patch('solum.common.repo_utils')
    @mock.patch('solum.deployer.handlers.heat.get_heat_client')
    def test_update_assembly_status(self, heat_clnt, mock_repo, mock_http,
                                    mock_clients, mock_ua, mock_wf_app):

        cfg.CONF.set_override('wait_interval', 1, group='deployer')
        cfg.CONF.set_override('growth_factor', 1, group='deployer')
        cfg.CONF.set_override('max_attempts', 1, group='deployer')

        handler = heat_handler.Handler()
        fake_assembly = fakes.FakeAssembly()
        stack = mock.MagicMock()
        stack.status = 'COMPLETE'
        heat_clnt.return_value.stacks.get.return_value = stack

        resp = {'status': '200'}
        conn = mock.MagicMock()
        conn.request.return_value = [resp, '']
        mock_http.return_value = conn

        cfg.CONF.deployer.du_attempts = 1

        mock_logger = mock.MagicMock()
        handler._parse_server_ip = mock.MagicMock(return_value=('xyz'))
        mock_repo.is_reachable.return_value = True
        handler._check_stack_status(self.ctx, fake_assembly.id, heat_clnt,
                                    'fake_id', [80], mock_logger)

        c1 = mock.call(self.ctx, fake_assembly.id,
                       {'status': STATES.STARTING_APP,
                        'application_uri': 'xyz:80'})

        c2 = mock.call(self.ctx, fake_assembly.id,
                       {'status': 'DEPLOYMENT_COMPLETE'})

        calls = [c1, c2]

        mock_ua.assert_has_calls(calls, any_order=False)

    @mock.patch('solum.deployer.handlers.heat.update_wf_and_app')
    @mock.patch('solum.deployer.handlers.heat.update_assembly')
    @mock.patch('solum.common.clients.OpenStackClients')
    @mock.patch('httplib2.Http')
    @mock.patch('solum.deployer.handlers.heat.get_heat_client')
    def test_update_assembly_status_multiple_ports(self, heat_clnt, mock_http,
                                                   mock_clients, mock_ua,
                                                   mock_wf_app):

        cfg.CONF.set_override('wait_interval', 1, group='deployer')
        cfg.CONF.set_override('growth_factor', 1, group='deployer')
        cfg.CONF.set_override('max_attempts', 1, group='deployer')

        handler = heat_handler.Handler()
        fake_assembly = fakes.FakeAssembly()
        stack = mock.MagicMock()
        stack.status = 'COMPLETE'
        heat_clnt.stacks.get.return_value = stack

        resp = {'status': '200'}
        conn = mock.MagicMock()
        conn.request.return_value = [resp, '']
        mock_http.return_value = conn

        cfg.CONF.deployer.du_attempts = 1

        mock_logger = mock.MagicMock()
        handler._parse_server_ip = mock.MagicMock(return_value=('xyz'))
        handler._check_stack_status(self.ctx, fake_assembly.id,
                                    heat_clnt.return_value,
                                    'fake_id', [80, 81], mock_logger)

        c1 = mock.call(self.ctx, fake_assembly.id,
                       {'status': STATES.STARTING_APP,
                        'application_uri': 'xyz:[80,81]'})

        c2 = mock.call(self.ctx, fake_assembly.id,
                       {'status': 'DEPLOYMENT_COMPLETE'})

        calls = [c1, c2]

        mock_ua.assert_has_calls(calls, any_order=False)

    @mock.patch('solum.deployer.handlers.heat.update_assembly')
    @mock.patch('solum.common.clients.OpenStackClients')
    @mock.patch('solum.deployer.handlers.heat.get_heat_client')
    def test_update_assembly_status_failed(self, heat_clnt,
                                           mock_clients, mock_ua):

        cfg.CONF.set_override('wait_interval', 1, group='deployer')
        cfg.CONF.set_override('growth_factor', 1, group='deployer')
        cfg.CONF.set_override('max_attempts', 1, group='deployer')

        handler = heat_handler.Handler()
        fake_assembly = fakes.FakeAssembly()
        stack = mock.MagicMock()
        stack.status = 'FAILED'
        heat_clnt.return_value.stacks.get.return_value = stack
        mock_logger = mock.MagicMock()
        handler._check_stack_status(self.ctx, fake_assembly.id,
                                    heat_clnt.return_value,
                                    'fake_id', [80], mock_logger)
        mock_ua.assert_called_once_with(self.ctx, fake_assembly.id,
                                        {'status':
                                         STATES.ERROR_STACK_CREATE_FAILED})

    @mock.patch('solum.deployer.handlers.heat.update_assembly')
    def test_get_template(self, mua):
        handler = heat_handler.Handler()
        fake_assembly = fakes.FakeAssembly()

        image_format = 'vm'
        image_storage = 'glance'
        image_loc = 'abc'
        image_name = 'def'
        ports = [80]
        mock_logger = mock.MagicMock()
        template = handler._get_template(self.ctx, image_format,
                                         image_storage, image_loc, image_name,
                                         fake_assembly, ports, mock_logger)
        self.assertIsNone(template)
        mua.assert_called_once_with(self.ctx,
                                    fake_assembly.id,
                                    {'status': STATES.ERROR})

    @mock.patch('solum.deployer.handlers.heat.update_assembly')
    def test_get_template_vm_glance(self, mock_update_assembly):
        handler = heat_handler.Handler()
        fake_assembly = fakes.FakeAssembly()

        image_format = 'vm'
        image_storage = 'glance'
        image_loc = 'abc'
        image_name = 'def'
        ports = [80]
        mock_logger = mock.MagicMock()
        template = handler._get_template(self.ctx, image_format,
                                         image_storage, image_loc, image_name,
                                         fake_assembly, ports, mock_logger)
        self.assertIsNone(template)
        mock_update_assembly.assert_called_once_with(self.ctx,
                                                     fake_assembly.id,
                                                     {'status': STATES.ERROR})

    @mock.patch('solum.common.catalog.get')
    def test_get_template_vm_docker_reg(self, mock_catalog_get):
        handler = heat_handler.Handler()
        fake_assembly = fakes.FakeAssembly()

        template_getter = mock.MagicMock()
        template_getter.return_value = self._get_fake_template()
        handler._get_template_for_docker_reg = template_getter

        image_format = 'vm'
        image_storage = 'docker_registry'
        image_loc = 'abc'
        image_name = 'def'
        ports = [80]
        mock_logger = mock.MagicMock()
        template = handler._get_template(self.ctx, image_format,
                                         image_storage, image_loc, image_name,
                                         fake_assembly, ports, mock_logger)
        self.assertIsNotNone(template)
        self.assertTrue(handler._get_template_for_docker_reg.called)
        mock_catalog_get.assert_called_once_with('templates', 'coreos')

    @mock.patch('solum.common.catalog.get')
    def test_get_template_vm_swift(self, mock_catalog_get):
        handler = heat_handler.Handler()
        fake_assembly = fakes.FakeAssembly()
        mock_logger = mock.MagicMock()

        image_format = 'vm'
        image_storage = 'swift'
        image_loc = 'abc'
        image_name = 'def'
        ports = [80]

        mock_catalog_get.return_value = self._get_fake_template()

        template = handler._get_template(self.ctx, image_format,
                                         image_storage, image_loc,
                                         image_name, fake_assembly,
                                         ports, mock_logger)

        self.assertEqual(self._get_fake_template(), template)
        self.assertEqual(1, mock_catalog_get.call_count)
        self.assertEqual(mock.call('templates', 'coreos'),
                         mock_catalog_get.call_args)

    @mock.patch('solum.deployer.handlers.heat.update_assembly')
    @mock.patch('solum.common.catalog.get')
    def test_get_template_vm_swift_error(self, mock_catalog_get, mock_ua):
        handler = heat_handler.Handler()
        fake_assembly = fakes.FakeAssembly()

        exc_obj = exception.ObjectNotFound()
        mock_catalog_get.side_effect = exc_obj

        template_getter = mock.MagicMock()
        template_getter.return_value = self._get_fake_template()
        handler._get_template_for_swift = template_getter

        image_format = 'vm'
        image_storage = 'swift'
        image_loc = 'abc'
        image_name = 'def'
        ports = [80]
        mock_logger = mock.MagicMock()
        template = handler._get_template(self.ctx, image_format,
                                         image_storage, image_loc, image_name,
                                         fake_assembly, ports, mock_logger)
        self.assertIsNone(template)
        mock_ua.assert_called_once_with(self.ctx, fake_assembly.id,
                                        {'status': STATES.ERROR})

        assert not handler._get_template_for_swift.called

    @mock.patch('solum.deployer.handlers.heat.update_assembly')
    @mock.patch('solum.common.catalog.get')
    def test_get_template_docker_read_error(self, mock_catalog_get, mock_ua):
        handler = heat_handler.Handler()
        fake_assembly = fakes.FakeAssembly()

        exc_obj = exception.ObjectNotFound()
        mock_catalog_get.side_effect = exc_obj

        template_getter = mock.MagicMock()
        template_getter.return_value = self._get_fake_template()
        handler._get_template_for_swift = template_getter

        image_format = 'docker'
        image_storage = 'swift'
        image_loc = 'abc'
        image_name = 'def'
        ports = [80]
        mock_logger = mock.MagicMock()
        template = handler._get_template(self.ctx, image_format,
                                         image_storage, image_loc, image_name,
                                         fake_assembly, ports, mock_logger)
        self.assertIsNone(template)
        mock_ua.assert_called_once_with(self.ctx, fake_assembly.id,
                                        {'status': STATES.ERROR})

    @mock.patch('solum.common.heat_utils.get_network_parameters')
    @mock.patch('solum.common.clients.OpenStackClients')
    def test_get_parameters_for_docker(self, mock_clients, mock_heat_utils):

        handler = heat_handler.Handler()
        fake_assembly = fakes.FakeAssembly()

        image_format = 'docker'
        image_loc = 'abc'
        image_name = 'abc'
        ports = [80]

        mock_logger = mock.MagicMock()

        params = handler._get_parameters(self.ctx, image_format,
                                         image_loc, image_name, fake_assembly,
                                         ports, mock_clients, mock_logger)

        self.assertEqual(fake_assembly.name, params['app_name'])
        self.assertEqual('abc', params['image'])
        self.assertEqual(80, params['port'])

    @mock.patch('solum.common.heat_utils.get_network_parameters')
    @mock.patch('solum.common.clients.OpenStackClients')
    def test_get_parameters_for_vm(self, mock_clients, mock_heat_utils):

        handler = heat_handler.Handler()
        fake_assembly = fakes.FakeAssembly()

        image_format = 'vm'
        image_loc = 'abc'
        image_name = 'abc'
        ports = [80]

        mock_logger = mock.MagicMock()

        cfg.CONF.set_override('flavor', 'abc', group='deployer')
        cfg.CONF.set_override('image', 'def', group='deployer')

        params = handler._get_parameters(self.ctx, image_format,
                                         image_loc, image_name, fake_assembly,
                                         ports, mock_clients, mock_logger)

        self.assertEqual(str(fake_assembly.uuid), params['name'])
        self.assertEqual('abc', params['flavor'])
        self.assertEqual('def', params['image'])
        self.assertIsNone(params.get('port'))

    @mock.patch('solum.deployer.handlers.heat.update_assembly')
    @mock.patch('solum.common.heat_utils.get_network_parameters')
    @mock.patch('solum.common.clients.OpenStackClients')
    def test_get_parameters_for_unrecognized_img_format(self, mock_clients,
                                                        mock_heat_utils,
                                                        mock_ua):

        handler = heat_handler.Handler()
        fake_assembly = fakes.FakeAssembly()

        image_format = 'abc'
        image_loc = 'abc'
        image_name = 'abc'
        ports = [80]

        mock_logger = mock.MagicMock()

        params = handler._get_parameters(self.ctx, image_format,
                                         image_loc, image_name, fake_assembly,
                                         ports, mock_clients, mock_logger)

        self.assertIsNone(params)

        mock_ua.assert_called_once_with(self.ctx, fake_assembly.id,
                                        {'status':
                                         STATES.ERROR})

    @mock.patch('solum.deployer.handlers.heat.update_assembly')
    def test_check_stack_status(self, mock_ua):
        handler = heat_handler.Handler()
        fake_assembly = fakes.FakeAssembly()

        mock_client = mock.MagicMock()
        mock_client.stacks.get.side_effect = Exception()

        cfg.CONF.set_override('wait_interval', 1, group='deployer')
        cfg.CONF.set_override('growth_factor', 1, group='deployer')
        cfg.CONF.set_override('max_attempts', 1, group='deployer')

        mock_logger = mock.MagicMock()
        handler._check_stack_status(self.ctx, fake_assembly.id, mock_client,
                                    'fake_id', [80], mock_logger)
        mock_ua.assert_called_once_with(self.ctx, fake_assembly.id,
                                        {'status':
                                         STATES.ERROR_STACK_CREATE_FAILED})

    def test_parse_server_ip(self):
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
        host_url = handler._parse_server_ip(heat_output)
        self.assertEqual("192.168.78.21", host_url)

    def test_find_id_if_stack_exists(self):
        handler = heat_handler.Handler()
        assem = mock.MagicMock
        assem.heat_stack_component = mock.MagicMock
        assem.heat_stack_component.heat_stack_id = '123'
        id = handler._find_id_if_stack_exists(assem)
        self.assertEqual('123', id)

    @mock.patch('solum.common.solum_swiftclient.SwiftClient.delete_object')
    @mock.patch('solum.objects.registry')
    @mock.patch('solum.deployer.handlers.heat.tlog')
    @mock.patch('solum.api.handlers.userlog_handler.UserlogHandler')
    def test_delete_app_artifacts_from_swift(self, mock_log_handler, m_log,
                                             mock_registry, mock_swift_delete):
        fake_assembly = fakes.FakeAssembly()
        fake_image = fakes.FakeImage()
        mock_registry.Image.get_by_id.return_value = fake_image
        handler = heat_handler.Handler()
        handler._delete_app_artifacts_from_swift(self.ctx, mock_log_handler,
                                                 fake_assembly)
        mock_registry.Image.get_by_id.assert_called_once_with(
            mock.ANY, fake_assembly.image_id)
        docker_image_name = fake_image.docker_image_name
        img_filename = docker_image_name.split('-', 1)[1]
        mock_swift_delete.assert_called_once_with('solum_du', img_filename)

    @mock.patch('solum.common.solum_swiftclient.SwiftClient.delete_object')
    @mock.patch('solum.objects.registry')
    @mock.patch('solum.deployer.handlers.heat.tlog')
    @mock.patch('solum.api.handlers.userlog_handler.UserlogHandler')
    def test_delete_app_artifacts_from_swift_no_image(self, mock_log_handler,
                                                      m_log, mock_registry,
                                                      mock_swift_delete):
        fake_assembly = fakes.FakeAssembly()
        fake_assembly.image_id = None
        handler = heat_handler.Handler()
        handler._delete_app_artifacts_from_swift(self.ctx, mock_log_handler,
                                                 fake_assembly)
        self.assertFalse(mock_registry.Image.get_by_id.called)
        self.assertFalse(mock_swift_delete.called)

    @mock.patch('solum.common.solum_swiftclient.SwiftClient.delete_object')
    @mock.patch('solum.api.handlers.userlog_handler.UserlogHandler')
    @mock.patch('solum.deployer.handlers.heat.tlog')
    @mock.patch('solum.objects.registry')
    @mock.patch('solum.common.clients.OpenStackClients')
    @mock.patch('solum.deployer.handlers.heat.get_heat_client')
    def test_destroy_success(self, heat_clnt, mock_client, mock_registry,
                             m_log, mock_log_handler, mock_swift_delete):
        cfg.CONF.set_override('image_storage', 'swift', group='worker')
        fake_assem = fakes.FakeAssembly()
        mock_registry.Assembly.get_by_id.return_value = fake_assem
        fake_image = fakes.FakeImage()
        mock_registry.Image.get_by_id.return_value = fake_image

        handler = heat_handler.Handler()

        mock_log = m_log.TenantLogger.return_value.log

        mock_del = heat_clnt.return_value.stacks.delete
        mock_del.side_effect = exc.HTTPNotFound

        cfg.CONF.deployer.max_attempts = 1
        cfg.CONF.deployer.wait_interval = 0
        cfg.CONF.deployer.growth_factor = 1.2

        with mock.patch.object(handler, "_find_id_if_stack_exists",
                               return_value=42):

            handler.destroy_assembly(self.ctx, fake_assem.id)

            self.assertTrue(mock_del.called)
            mock_registry.Image.get_by_id.assert_called_once_with(
                mock.ANY, fake_assem.image_id)
            docker_image_name = fake_image.docker_image_name
            img_filename = docker_image_name.split('-', 1)[1]
            mock_swift_delete.assert_called_once_with('solum_du', img_filename)
            log_handler = mock_log_handler.return_value
            log_handler.delete.assert_called_once_with(fake_assem.uuid)
            self.assertTrue(mock_log.called)

    @mock.patch('solum.common.solum_swiftclient.SwiftClient.delete_object')
    @mock.patch('solum.api.handlers.userlog_handler.UserlogHandler')
    @mock.patch('solum.deployer.handlers.heat.tlog')
    @mock.patch('solum.objects.registry')
    @mock.patch('solum.common.clients.OpenStackClients')
    @mock.patch('solum.deployer.handlers.heat.get_heat_client')
    def test_destroy_stack_not_found(self, heat_clnt, mock_client,
                                     mock_registry, m_log,
                                     mock_log_handler, mock_swift_delete):
        cfg.CONF.set_override('image_storage', 'swift', group='worker')
        fake_assem = fakes.FakeAssembly()
        mock_registry.Assembly.get_by_id.return_value = fake_assem
        fake_image = fakes.FakeImage()
        mock_registry.Image.get_by_id.return_value = fake_image

        handler = heat_handler.Handler()

        mock_log = m_log.TenantLogger.return_value.log

        mock_del = heat_clnt.return_value.stacks.delete
        mock_del.side_effect = exc.HTTPNotFound

        cfg.CONF.deployer.max_attempts = 1
        cfg.CONF.deployer.wait_interval = 0
        cfg.CONF.deployer.growth_factor = 1.2

        with mock.patch.object(handler, "_find_id_if_stack_exists",
                               return_value=42) as mock_find:

            handler.destroy_assembly(self.ctx, fake_assem.id)

            self.assertTrue(mock_find.called)
            self.assertTrue(mock_del.called)
            mock_registry.Image.get_by_id.assert_called_once_with(
                mock.ANY, fake_assem.image_id)
            docker_image_name = fake_image.docker_image_name
            img_filename = docker_image_name.split('-', 1)[1]
            mock_swift_delete.assert_called_once_with('solum_du', img_filename)
            log_handler = mock_log_handler.return_value
            log_handler.delete.assert_called_once_with(fake_assem.uuid)
            self.assertTrue(mock_log.called)

    @mock.patch('solum.deployer.handlers.heat.tlog')
    @mock.patch('solum.deployer.handlers.heat.update_assembly')
    @mock.patch('solum.objects.registry')
    @mock.patch('solum.common.clients.OpenStackClients')
    @mock.patch('solum.deployer.handlers.heat.get_heat_client')
    def test_destroy_error(self, heat_clnt, mock_client,
                           mock_registry, mua, m_log):
        fake_assem = fakes.FakeAssembly()
        mock_registry.Assembly.get_by_id.return_value = fake_assem

        mock_del = heat_clnt.return_value.stacks.delete

        handler = heat_handler.Handler()
        handler._find_id_if_stack_exists = mock.MagicMock(return_value='42')

        cfg.CONF.deployer.max_attempts = 1
        cfg.CONF.deployer.wait_interval = 0
        cfg.CONF.deployer.growth_factor = 1.2

        with mock.patch.object(handler, "_find_id_if_stack_exists",
                               return_value="42"):

            handler.destroy_assembly(self.ctx, fake_assem.id)

            c1 = mock.call(self.ctx, fake_assem.id,
                           {'status': STATES.DELETING})

            c2 = mock.call(self.ctx, fake_assem.id,
                           {'status': STATES.ERROR_STACK_DELETE_FAILED})

            calls = [c1, c2]

            mua.assert_has_calls(calls, any_order=False)

        self.assertTrue(mock_del.called)

    @mock.patch('solum.common.solum_swiftclient.SwiftClient.delete_object')
    @mock.patch('solum.api.handlers.userlog_handler.UserlogHandler')
    @mock.patch('solum.deployer.handlers.heat.tlog')
    @mock.patch('solum.objects.registry')
    @mock.patch('solum.common.clients.OpenStackClients')
    def test_destroy_absent_no_wf(self, mock_client, mock_registry,
                                  mock_tlogger, mock_log_handler,
                                  mock_swift_delete):

        cfg.CONF.worker.image_storage = "swift"
        fake_assem = fakes.FakeAssembly()
        mock_registry.Assembly.get_by_id.return_value = fake_assem
        fake_image = fakes.FakeImage()
        mock_registry.Image.get_by_id.return_value = fake_image

        nfe = exception.ResourceNotFound(name=fake_assem.name,
                                         id=fake_assem.id)
        mock_registry.Workflow.get_by_assembly_id.side_effect = nfe

        mock_log = mock_tlogger.TenantLogger.return_value.log
        mock_upload = mock_tlogger.TenantLogger.return_value.upload
        mock_log_del = mock_log_handler.return_value.delete
        mock_heat = mock_client.return_value.heat
        mock_del = mock_heat.return_value.stacks.delete

        hh = heat_handler.Handler()
        with mock.patch.object(hh, "_find_id_if_stack_exists",
                               return_value=None):

            hh.destroy_assembly(self.ctx, fake_assem.id)

        self.assertFalse(mock_del.called)
        self.assertTrue(fake_assem.destroy.called)
        mock_registry.Image.get_by_id.assert_called_once_with(
            mock.ANY, fake_assem.image_id)
        docker_image_name = fake_image.docker_image_name
        img_filename = docker_image_name.split('-', 1)[1]
        mock_swift_delete.assert_called_once_with('solum_du', img_filename)
        self.assertTrue(mock_log.called)
        self.assertTrue(mock_upload.called)
        self.assertEqual(1, mock_log_del.call_count)
        self.assertEqual(mock.call(fake_assem.uuid), mock_log_del.call_args)

    @mock.patch('solum.common.solum_swiftclient.SwiftClient.delete_object')
    @mock.patch('solum.api.handlers.userlog_handler.UserlogHandler')
    @mock.patch('solum.deployer.handlers.heat.tlog')
    @mock.patch('solum.objects.registry')
    @mock.patch('solum.common.clients.OpenStackClients')
    def test_destroy_absent_wf_present(self, mock_client, mock_registry,
                                       mock_tlogger, mock_log_handler,
                                       mock_swift_delete):

        cfg.CONF.worker.image_storage = "swift"
        fake_assem = fakes.FakeAssembly()
        mock_registry.Assembly.get_by_id.return_value = fake_assem
        fake_image = fakes.FakeImage()
        mock_registry.Image.get_by_id.return_value = fake_image

        fake_wf = fakes.FakeWorkflow()
        mock_registry.Workflow.get_by_assembly_id.side_effect = fake_wf

        mock_log = mock_tlogger.TenantLogger.return_value.log
        mock_upload = mock_tlogger.TenantLogger.return_value.upload
        mock_log_del = mock_log_handler.return_value.delete
        mock_heat = mock_client.return_value.heat
        mock_del = mock_heat.return_value.stacks.delete

        hh = heat_handler.Handler()
        with mock.patch.object(hh, "_find_id_if_stack_exists",
                               return_value=None):

            hh.destroy_assembly(self.ctx, fake_assem.id)

        self.assertFalse(mock_del.called)
        self.assertFalse(fake_assem.destroy.called)
        mock_registry.Image.get_by_id.assert_called_once_with(
            mock.ANY, fake_assem.image_id)
        docker_image_name = fake_image.docker_image_name
        img_filename = docker_image_name.split('-', 1)[1]
        mock_swift_delete.assert_called_once_with('solum_du', img_filename)
        self.assertTrue(mock_log.called)
        self.assertTrue(mock_upload.called)
        self.assertEqual(1, mock_log_del.call_count)
        self.assertEqual(mock.call(fake_assem.uuid), mock_log_del.call_args)

    @mock.patch('solum.objects.registry')
    @mock.patch('solum.common.clients.OpenStackClients')
    @mock.patch('solum.deployer.handlers.heat.get_heat_client')
    def test_successful_deploy_destroys_twins(self, heat_clnt,
                                              mock_client, mr):
        handler = heat_handler.Handler()
        old_app = fakes.FakeAssembly()
        old_app.name = 'old app'
        old_app.status = 'DEPLOYMENT_COMPLETE'

        new_app = fakes.FakeAssembly()
        new_app.id = 9
        new_app.plan_id = old_app.plan_id
        new_app.name = 'new app'
        new_app.status = 'DEPLOYMENT_COMPLETE'

        cfg.CONF.set_override('wait_interval', 0, group='deployer')
        cfg.CONF.set_override('growth_factor', 0, group='deployer')
        cfg.CONF.set_override('max_attempts', 1, group='deployer')

        self.assertEqual(old_app.plan_id, new_app.plan_id)
        self.assertEqual(old_app.plan_uuid, new_app.plan_uuid)
        mr.AssemblyList.get_earlier.return_value = [old_app]

        mock_st_del = heat_clnt.return_value.stacks.delete
        mock_st_get = heat_clnt.return_value.stacks.get

        handler.destroy_assembly = mock.MagicMock()
        handler._destroy_other_assemblies(self.ctx, new_app.id,
                                          heat_clnt.return_value)
        self.assertTrue(mock_st_del.called)
        self.assertTrue(mock_st_get.called)

    @mock.patch('solum.objects.registry')
    @mock.patch('solum.common.clients.OpenStackClients')
    @mock.patch('solum.deployer.handlers.heat.get_heat_client')
    def test_successful_deploy_preserves_others(self, heat_clnt,
                                                mock_client, mr):
        handler = heat_handler.Handler()
        old_app = fakes.FakeAssembly()
        old_app.name = 'old app'
        old_app.plan_id = 1
        old_app.id = 1
        old_app.status = 'DEPLOYMENT_COMPLETE'

        new_app = fakes.FakeAssembly()
        new_app.id = 1
        new_app.plan_id = 2
        new_app.plan_uuid = 'new fake plan uuid'
        new_app.name = 'new app'
        new_app.status = 'DEPLOYMENT_COMPLETE'

        cfg.CONF.set_override('wait_interval', 0, group='deployer')
        cfg.CONF.set_override('growth_factor', 0, group='deployer')
        cfg.CONF.set_override('max_attempts', 1, group='deployer')

        self.assertNotEqual(old_app.plan_id, new_app.plan_id)
        self.assertNotEqual(old_app.plan_uuid, new_app.plan_uuid)
        mr.AssemblyList.get_earlier.return_value = [old_app]

        mr.Assembly.get_by_id.return_value = new_app

        mock_heat = mock_client.return_value.heat
        mock_st_del = mock_heat.return_value.stacks.delete
        mock_st_get = mock_heat.return_value.stacks.get

        handler.destroy_assembly = mock.MagicMock()
        handler._destroy_other_assemblies(self.ctx, new_app.id, heat_clnt)
        self.assertFalse(mock_st_del.called)
        self.assertFalse(mock_st_get.called)

    @mock.patch('solum.objects.registry')
    @mock.patch('solum.deployer.handlers.heat.get_heat_client')
    def test_successful_deploy_preserves_notreadies(self, heat_clnt, mr):
        handler = heat_handler.Handler()
        old_app = fakes.FakeAssembly()
        old_app.name = 'old app'
        old_app.status = 'BUILDING'

        new_app = fakes.FakeAssembly()
        new_app.id = 9
        new_app.plan_id = old_app.plan_id
        new_app.name = 'new app'
        new_app.status = 'DEPLOYMENT_COMPLETE'

        self.assertEqual(old_app.plan_id, new_app.plan_id)
        self.assertEqual(old_app.plan_uuid, new_app.plan_uuid)
        mr.AssemblyList.get_earlier.return_value = []

        handler.destroy_assembly = mock.MagicMock()
        handler._destroy_other_assemblies(self.ctx, new_app.id, heat_clnt)
        self.assertEqual(0, handler.destroy_assembly.call_count)

    @mock.patch('solum.objects.registry')
    @mock.patch('solum.deployer.handlers.heat.get_heat_client')
    def test_unsuccessful_deploy_preserves_everyone(self, heat_clnt, mr):
        handler = heat_handler.Handler()
        old_app = fakes.FakeAssembly()
        old_app.name = 'old app'
        old_app.status = 'DEPLOYMENT_COMPLETE'

        new_app = fakes.FakeAssembly()
        new_app.id = 9
        new_app.plan_id = old_app.plan_id
        new_app.name = 'new app'
        new_app.status = 'ERROR'

        self.assertEqual(old_app.plan_id, new_app.plan_id)
        self.assertEqual(old_app.plan_uuid, new_app.plan_uuid)
        mr.AssemblyList.get_earlier.return_value = []

        handler.destroy_assembly = mock.MagicMock()
        handler._destroy_other_assemblies(self.ctx, new_app.id,
                                          heat_clnt.return_value)
        self.assertEqual(0, handler.destroy_assembly.call_count)

    def _get_key(self):
        return "robust-du-handling.sh"

    def _get_fake_template(self):
        t = "description: test\n"
        t += "resources:\n"
        t += "  compute_instance:\n"
        t += "    properties:\n"
        t += "      user_data:\n"
        t += "        str_replace:\n"
        t += "          {template:"
        t += "            #!/bin/bash -x\n"
        t += "            #Invoke the container\n"
        t += "}\n"
        return t

    def _get_tmpl_for_docker_reg(self, assem, template, image_id):
        template_bdy = yaml.safe_load(template)

        run_docker = ('#!/bin/bash -x\n'
                      '# Invoke the container\n'
                      'docker run -p 80:80 -d {img}\n'
                      'wc_notify --data-binary {stat}')
        run_docker = run_docker.format(img=image_id,
                                       stat='\'{"status": "SUCCESS"}\'')
        comp_instance = template_bdy['resources']['compute_instance']
        user_data = comp_instance['properties']['user_data']
        user_data['str_replace']['template'] = run_docker
        comp_instance['properties']['user_data'] = user_data
        template_bdy['resources']['compute_instance'] = comp_instance
        template = yaml.dump(template_bdy)
        return template

    def _get_tmpl_for_swift(self, assem, template, image_loc, image_name):
        template_bdy = yaml.safe_load(template)

        image_tar_location = image_loc

        run_docker = ('#!/bin/bash -x\n'
                      '# Invoke the container\n'
                      'wget \"{image_tar_location}\" --output-document={du}\n'
                      'docker load < {du}\n'
                      'docker run -p 80:80 -d {du}\n'
                      'wc_notify --data-binary {stat}')
        run_docker = run_docker.format(image_tar_location=image_tar_location,
                                       du=image_name,
                                       stat='\'{"status": "SUCCESS"}\'')

        comp_instance = template_bdy['resources']['compute_instance']
        user_data = comp_instance['properties']['user_data']
        user_data['str_replace']['template'] = run_docker
        comp_instance['properties']['user_data'] = user_data
        template_bdy['resources']['compute_instance'] = comp_instance
        template = yaml.safe_dump(template_bdy,
                                  encoding='utf-8',
                                  allow_unicode=True)
        return template
