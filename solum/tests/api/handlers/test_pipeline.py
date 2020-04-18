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


from solum.api.handlers import pipeline_handler
from solum.common import catalog
from solum.common import exception
from solum.common import yamlutils
from solum.tests import base
from solum.tests import fakes
from solum.tests import utils

from oslo_utils import uuidutils


@mock.patch('solum.objects.registry')
class TestPipelineHandler(base.BaseTestCase):
    def setUp(self):
        super(TestPipelineHandler, self).setUp()
        self.ctx = utils.dummy_context()

    def test_pipeline_get(self, mock_registry):
        mock_registry.return_value.Pipeline.get_by_uuid.return_value = {
            'plan_id': '1234'
        }
        handler = pipeline_handler.PipelineHandler(self.ctx)
        res = handler.get('test_id')
        self.assertIsNotNone(res)
        mock_registry.Pipeline.get_by_uuid.assert_called_once_with(
            self.ctx, 'test_id')

    def test_pipeline_get_all(self, mock_registry):
        mock_registry.PipelineList.get_all.return_value = {}
        handler = pipeline_handler.PipelineHandler(self.ctx)
        res = handler.get_all()
        self.assertIsNotNone(res)
        mock_registry.PipelineList.get_all.assert_called_once_with(self.ctx)

    def test_update(self, mock_registry):
        data = {'user_id': 'new_user_id',
                'plan_uuid': 'input_plan_uuid'}
        handler = pipeline_handler.PipelineHandler(self.ctx)
        handler.update('test_id', data)
        mock_registry.Pipeline.update_and_save.assert_called_once_with(
            self.ctx, 'test_id', data)

    @mock.patch('solum.common.clients.OpenStackClients.keystone')
    def test_create(self, mock_kc, mock_registry):
        data = {'user_id': 'new_user_id',
                'uuid': 'input_uuid',
                'plan_uuid': 'input_plan_uuid'}

        db_obj = fakes.FakePipeline()
        mock_registry.Pipeline.return_value = db_obj
        fp = fakes.FakePlan()
        mock_registry.Plan.get_by_id.return_value = fp
        fp.raw_content = {
            'name': 'theplan',
            'artifacts': [{'name': 'nodeus',
                           'artifact_type': 'application.heroku',
                           'content': {
                               'href': 'https://example.com/ex.git'},
                           'language_pack': 'auto'}]}
        trust_ctx = utils.dummy_context()
        trust_ctx.trust_id = '12345'
        mock_kc.return_value.create_trust_context.return_value = trust_ctx

        handler = pipeline_handler.PipelineHandler(self.ctx)
        handler._execute_workbook = mock.MagicMock()
        handler._ensure_workbook = mock.MagicMock()
        res = handler.create(data)
        db_obj.update.assert_called_once_with(data)
        handler._execute_workbook.assert_called_once_with(db_obj)
        handler._ensure_workbook.assert_called_once_with(db_obj)
        db_obj.create.assert_called_once_with(self.ctx)
        self.assertEqual(db_obj, res)
        mock_kc.return_value.create_trust_context.assert_called_once_with()

    @mock.patch('solum.common.clients.OpenStackClients')
    @mock.patch('solum.common.catalog.get')
    def test_empty_create_stack(self, mock_get, mock_clients, mock_registry):
        db_obj = fakes.FakePipeline()
        test_name = uuidutils.generate_uuid()
        test_id = uuidutils.generate_uuid()
        db_obj.name = test_name
        mock_registry.Pipeline.return_value = db_obj

        fake_template = json.dumps({})
        mock_get.return_value = fake_template

        mock_create = mock_clients.return_value.heat.return_value.stacks.create
        mock_create.return_value = {"stack": {"id": test_id,
                                    "links": [{"href": "http://fake.ref",
                                               "rel": "self"}]}}
        handler = pipeline_handler.PipelineHandler(self.ctx)
        res = handler._create_empty_stack(db_obj)
        mock_create.assert_called_once_with(stack_name=test_name,
                                            template=fake_template)
        self.assertEqual(test_id, res)

    @mock.patch('solum.common.clients.OpenStackClients')
    def test_delete(self, mock_clients, mock_registry):
        db_obj = fakes.FakePipeline()
        mock_exec = mock.MagicMock()
        mock_exec.context = json.dumps({'stack_id': 'foo'})
        mock_mistral = mock_clients.return_value.mistral.return_value
        mock_mistral.executions.get.return_value = mock_exec
        wb = yamlutils.dump({'Workflow': {
            'tasks': {'start':
                      {'parameters': {'stack_id': ''}}}}})
        mock_mistral.workbooks.get_definition.return_value = wb

        mock_registry.Pipeline.get_by_uuid.return_value = db_obj
        handler = pipeline_handler.PipelineHandler(self.ctx)
        handler.delete('test_id')
        db_obj.destroy.assert_called_once_with(self.ctx)
        mock_registry.Pipeline.get_by_uuid.assert_called_once_with(self.ctx,
                                                                   'test_id')

        mock_heat = mock_clients.return_value.heat.return_value
        mock_heat.stacks.delete.assert_called_once_with(stack_id='foo')

        mock_kc = mock_clients.return_value.keystone.return_value
        mock_kc.delete_trust.assert_called_once_with('trust_worthy')

    def test_trigger_workflow(self, mock_registry):
        trigger_id = 1
        db_obj = fakes.FakePipeline()
        mock_registry.Pipeline.get_by_trigger_id.return_value = db_obj
        plan_obj = fakes.FakePlan()
        mock_registry.Plan.get_by_id.return_value = plan_obj
        handler = pipeline_handler.PipelineHandler(self.ctx)
        handler._execute_workbook = mock.MagicMock()
        handler._context_from_trust_id = mock.MagicMock(return_value=self.ctx)
        handler.trigger_workflow(trigger_id)
        handler._execute_workbook.assert_called_once_with(db_obj)
        handler._context_from_trust_id.assert_called_once_with('trust_worthy')
        mock_registry.Pipeline.get_by_trigger_id.assert_called_once_with(
            None, trigger_id)

    @mock.patch('solum.common.clients.OpenStackClients')
    def test_get_context_from_last_execution(self, mock_clients,
                                             mock_registry):
        fpipe = fakes.FakePipeline()
        mock_exec = mock.MagicMock()
        mock_exec.context = json.dumps({'stack_id': 'foo',
                                        'build_service_url': 'url-for',
                                        'base_image_id': '1-2-3-4',
                                        'source_format': 'heroku'})
        mock_mistral = mock_clients.return_value.mistral.return_value
        mock_mistral.executions.get.return_value = mock_exec
        wbook = catalog.get('workbooks', 'build_deploy')
        mock_mistral.workbooks.get_definition.return_value = wbook

        handler = pipeline_handler.PipelineHandler(self.ctx)

        ex_ctx = handler._get_context_from_last_execution(fpipe)
        self.assertEqual('foo', ex_ctx['stack_id'])
        self.assertEqual('url-for', ex_ctx['build_service_url'])
        self.assertEqual('1-2-3-4', ex_ctx['base_image_id'])
        self.assertEqual('heroku', ex_ctx['source_format'])

    @mock.patch('solum.common.heat_utils.get_network_parameters')
    @mock.patch('solum.common.clients.OpenStackClients.keystone')
    def test_build_execution_context_first_run(self, mock_ks, mock_net,
                                               mock_registry):
        fpipe = fakes.FakePipeline()
        fplan = fakes.FakePlan()
        mock_net.return_value = {'public_net': 'fake-net-id'}
        mock_registry.Plan.get_by_id.return_value = fplan
        fplan.raw_content = {
            'name': 'theplan',
            'artifacts': [{'name': 'nodeus',
                           'artifact_type': 'heroku',
                           'content': {
                               'href': 'https://example.com/ex.git'},
                           'language_pack': '1-2-3-4'}]}

        handler = pipeline_handler.PipelineHandler(self.ctx)

        handler._get_context_from_last_execution = mock.MagicMock(
            return_value=None)

        handler._create_empty_stack = mock.MagicMock(return_value='foo')
        url_for = mock_ks.return_value.client.service_catalog.url_for
        url_for.return_value = 'url-for'
        ex_ctx = handler._build_execution_context(fpipe)
        self.assertEqual('foo', ex_ctx['stack_id'])
        self.assertEqual('url-for', ex_ctx['build_service_url'])
        self.assertEqual('1-2-3-4', ex_ctx['base_image_id'])
        self.assertEqual('heroku', ex_ctx['source_format'])
        self.assertEqual('faker', ex_ctx['parameters']['app_name'])
        self.assertEqual('fake-net-id', ex_ctx['parameters']['public_net'])

    @mock.patch('solum.common.clients.OpenStackClients')
    def test_build_execution_context_next_run(self, mock_clients,
                                              mock_registry):
        fpipe = fakes.FakePipeline()
        fplan = fakes.FakePlan()
        mock_registry.Plan.get_by_id.return_value = fplan
        fplan.raw_content = {
            'name': 'theplan',
            'artifacts': [{'name': 'nodeus',
                           'artifact_type': 'heroku',
                           'content': {
                               'href': 'https://example.com/ex.git'},
                           'language_pack': '1-2-3-4'}]}

        mock_exec = mock.MagicMock()
        mock_exec.context = json.dumps(
            {'stack_id': 'foo',
             'build_service_url': 'url-for',
             'base_image_id': '1-2-3-4',
             'source_format': 'heroku',
             'parameters': {'app_name': 'fruit',
                            'public_net': 'nsa-2-0'}})
        mock_mistral = mock_clients.return_value.mistral.return_value
        mock_mistral.executions.get.return_value = mock_exec
        wbook = catalog.get('workbooks', 'build_deploy')
        mock_mistral.workbooks.get_definition.return_value = wbook

        handler = pipeline_handler.PipelineHandler(self.ctx)

        ex_ctx = handler._build_execution_context(fpipe)
        self.assertEqual('foo', ex_ctx['stack_id'])
        self.assertEqual('url-for', ex_ctx['build_service_url'])
        self.assertEqual('1-2-3-4', ex_ctx['base_image_id'])
        self.assertEqual('heroku', ex_ctx['source_format'])
        self.assertEqual('fruit', ex_ctx['parameters']['app_name'])
        self.assertEqual('nsa-2-0', ex_ctx['parameters']['public_net'])

    @mock.patch('solum.common.clients.OpenStackClients')
    def test_ensure_workbook_exists(self, mock_clients, mock_registry):
        fpipe = fakes.FakePipeline()
        fpipe.workbook_name = 'build'
        mock_mistral = mock_clients.return_value.mistral.return_value
        wbook = mock.MagicMock()
        wbook.workbook_name = 'build'
        mock_mistral.workbooks.get.return_value = wbook
        handler = pipeline_handler.PipelineHandler(self.ctx)
        handler._ensure_workbook(fpipe)
        mock_mistral.workbooks.create.assert_has_calls([])

    @mock.patch('solum.common.clients.OpenStackClients')
    def test_ensure_workbook_not_exists(self, mock_clients, mock_registry):
        fpipe = fakes.FakePipeline()
        fpipe.workbook_name = 'build'
        mock_mistral = mock_clients.return_value.mistral.return_value
        mock_mistral.workbooks.get.side_effect = ValueError(
            'Workbook not found')
        handler = pipeline_handler.PipelineHandler(self.ctx)
        handler._ensure_workbook(fpipe)

        mock_mistral.workbooks.create.assert_called_once_with(
            'build', 'solum generated workbook', ['solum', 'builtin'])
        wbook = catalog.get('workbooks', 'build')
        mock_mistral.workbooks.upload_definition.assert_called_once_with(
            'build', wbook)

    @mock.patch('solum.common.clients.OpenStackClients')
    @mock.patch('solum.common.catalog.get')
    def test_ensure_workbook_unknown(self, mock_get,
                                     mock_clients, mock_registry):
        fpipe = fakes.FakePipeline()
        fpipe.workbook_name = 'we-dont-have-this'
        mock_mistral = mock_clients.return_value.mistral.return_value
        mock_mistral.workbooks.get.side_effect = ValueError(
            'Workbook not found')
        mock_get.side_effect = exception.ObjectNotFound(
            name='workbook', id='we-dont-have-this')
        handler = pipeline_handler.PipelineHandler(self.ctx)
        self.assertRaises(exception.ObjectNotFound,
                          handler._ensure_workbook, fpipe)
