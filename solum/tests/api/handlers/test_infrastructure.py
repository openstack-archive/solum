# Copyright 2014 - Numergy
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


from solum.api.handlers import infrastructure_handler as infra
from solum.tests import base
from solum.tests import fakes
from solum.tests import utils


@mock.patch('solum.objects.registry')
class TestInfrastructureStackHandler(base.BaseTestCase):

    def setUp(self):
        super(TestInfrastructureStackHandler, self).setUp()
        self.ctx = utils.dummy_context()

    def test_get(self, mock_registry):
        mock_registry.InfrastructureStack.get_by_uuid.return_value = {}
        handler = infra.InfrastructureStackHandler(self.ctx)
        res = handler.get('test_id')
        self.assertIsNotNone(res)
        mock_registry.InfrastructureStack.get_by_uuid.assert_called_once_with(
            self.ctx, 'test_id')

    def test_get_all(self, mock_registry):
        mock_registry.StackList.get_all.return_value = {}
        handler = infra.InfrastructureStackHandler(self.ctx)
        res = handler.get_all()
        self.assertIsNotNone(res)
        mock_registry.InfrastructureStackList.get_all.assert_called_once_with(
            self.ctx)

    def test_update(self, mock_reg):
        data = {'user_id': 'new_user_id',
                'image_id': 'new_image_id',
                'heat_stack_id': 'new_stack_id'}
        handler = infra.InfrastructureStackHandler(self.ctx)
        handler.update('test_id', data)
        mock_reg.InfrastructureStack.update_and_save.assert_called_once_with(
            self.ctx, 'test_id', data)

    @mock.patch('solum.common.clients.OpenStackClients')
    @mock.patch('solum.common.catalog.get')
    def test_create(self, mock_get, mock_clients, mock_registry):
        data = {'user_id': 'new_user_id',
                'image_id': 'new_image_id'}
        db_obj = fakes.FakeInfrastructureStack()
        fake_template = json.dumps({'description': 'test'})
        mock_get.return_value = fake_template
        parameters = {'image': 'new_image_id'}
        mock_registry.InfrastructureStack.return_value = db_obj
        mock_create = mock_clients.return_value.heat.return_value.stacks.create
        mock_create.return_value = {"stack": {"id": "fake_id",
                                    "links": [{"href": "http://fake.ref",
                                               "rel": "self"}]}}
        mock_queue = mock_clients.return_value.zaqar.return_value.queue
        handler = infra.InfrastructureStackHandler(self.ctx)
        res = handler.create(data)
        db_obj.update.assert_called_once_with(data)
        db_obj.create.assert_called_once_with(self.ctx)
        self.assertEqual(db_obj, res)
        mock_create.assert_called_once_with(stack_name='infra',
                                            template=fake_template,
                                            parameters=parameters)
        mock_queue.assert_called_once_with(db_obj.uuid)

    @mock.patch('solum.common.clients.OpenStackClients')
    def test_create_zaqar_queue(self, mock_clients, mock_registry):
        queue_name = 'test'
        mock_queue = mock_clients.return_value.zaqar.return_value.queue
        handler = infra.InfrastructureStackHandler(self.ctx)
        handler._create_zaqar_queue(queue_name)
        mock_queue.assert_called_once_with(queue_name)

    def test_delete(self, mock_registry):
        db_obj = fakes.FakeInfrastructureStack()
        mock_registry.InfrastructureStack.get_by_uuid.return_value = db_obj
        handler = infra.InfrastructureStackHandler(self.ctx)
        handler.delete('test_id')
        db_obj.destroy.assert_called_once_with(self.ctx)
        mock_registry.InfrastructureStack.get_by_uuid.assert_called_once_with(
            self.ctx, 'test_id')
