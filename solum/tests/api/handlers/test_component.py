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

from solum.api.handlers import component_handler
from solum.tests import base
from solum.tests import fakes


@mock.patch('solum.objects.registry')
class TestComponentHandler(base.BaseTestCase):
    def test_component_get(self, mock_registry):
        mock_registry.component.get_by_uuid.return_value = {}
        handler = component_handler.ComponentHandler()
        res = handler.get('test_id')
        self.assertIsNotNone(res)
        mock_registry.Component.get_by_uuid.\
            assert_called_once_with(None, 'test_id')

    def test_get_all(self, mock_registry):
        mock_registry.ComponentList.get_all.return_value = {}
        handler = component_handler.ComponentHandler()
        res = handler.get_all()
        self.assertIsNotNone(res)
        mock_registry.ComponentList.get_all.assert_called_once_with(None)

    def test_update(self, mock_registry):
        data = {'user_id': 'new_user_id'}
        db_obj = fakes.FakeComponent()
        mock_registry.Component.get_by_uuid.return_value = db_obj
        handler = component_handler.ComponentHandler()
        res = handler.update('test_id', data)
        self.assertEqual(db_obj.user_id, res.user_id)
        db_obj.save.assert_called_once_with(None)
        mock_registry.Component.get_by_uuid.assert_called_once_with(None,
                                                                    'test_id')

    def test_create(self, mock_registry):
        data = {'user_id': 'new_user_id'}
        handler = component_handler.ComponentHandler()
        res = handler.create(data)
        self.assertEqual('new_user_id', res.user_id)

    def test_delete(self, mock_registry):
        db_obj = fakes.FakeComponent()
        mock_registry.Component.get_by_uuid.return_value = db_obj
        handler = component_handler.ComponentHandler()
        handler.delete('test_id')
        db_obj.destroy.assert_called_once_with(None)
        mock_registry.Component.get_by_uuid.assert_called_once_with(None,
                                                                    'test_id')
