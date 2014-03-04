# -*- coding: utf-8 -*-
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

from solum.api.handlers import service_handler
from solum.tests import base
from solum.tests import fakes


@mock.patch('solum.objects.registry')
class TestServiceHandler(base.BaseTestCase):
    def test_get(self, mock_registry):
        mock_registry.Service.get_by_uuid.return_value = {}
        handler = service_handler.ServiceHandler()
        res = handler.get('test_id')
        self.assertIsNotNone(res)
        mock_registry.Service.get_by_uuid.\
            assert_called_once_with(None, 'test_id')

    def test_get_all(self, mock_registry):
        mock_registry.ServiceList.get_all.return_value = {}
        handler = service_handler.ServiceHandler()
        res = handler.get_all()
        self.assertIsNotNone(res)
        mock_registry.ServiceList.get_all.assert_called_once_with(None)

    def test_update(self, mock_registry):
        data = {'user_id': 'new_user_id'}
        db_obj = fakes.FakeService()
        mock_registry.Service.get_by_uuid.return_value = db_obj
        handler = service_handler.ServiceHandler()
        res = handler.update('test_id', data)
        self.assertEqual(db_obj.user_id, res.user_id)
        db_obj.save.assert_called_once_with(None)
        mock_registry.Service.get_by_uuid.assert_called_once_with(None,
                                                                  'test_id')

    def test_create(self, mock_registry):
        data = {'user_id': 'new_user_id',
                'uuid': 'input_uuid'}
        handler = service_handler.ServiceHandler()
        res = handler.create(data)
        self.assertEqual('new_user_id', res.user_id)
        self.assertNotEqual('uuid', res.uuid)

    def test_delete(self, mock_registry):
        db_obj = fakes.FakeService()
        mock_registry.Service.get_by_uuid.return_value = db_obj
        handler = service_handler.ServiceHandler()
        handler.delete('test_id')
        db_obj.destroy.assert_called_once_with(None)
        mock_registry.Service.get_by_uuid.assert_called_once_with(None,
                                                                  'test_id')
