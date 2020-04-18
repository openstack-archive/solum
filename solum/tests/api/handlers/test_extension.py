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

from solum.api.handlers import extension_handler as extension
from solum.tests import base
from solum.tests import fakes
from solum.tests import utils


@mock.patch('solum.objects.registry')
class TestExtensionHandler(base.BaseTestCase):
    def setUp(self):
        super(TestExtensionHandler, self).setUp()
        self.ctx = utils.dummy_context()

    def test_extension_get(self, mock_registry):
        mock_registry.Extension.get_by_uuid.return_value = {}
        handler = extension.ExtensionHandler(self.ctx)
        res = handler.get('test_id')
        self.assertIsNotNone(res)
        mock_registry.Extension.get_by_uuid.assert_called_once_with(self.ctx,
                                                                    'test_id')

    def test_extension_get_all(self, mock_registry):
        mock_registry.ExtensionList.get_all.return_value = {}
        handler = extension.ExtensionHandler(self.ctx)
        res = handler.get_all()
        self.assertIsNotNone(res)
        mock_registry.ExtensionList.get_all.assert_called_once_with(self.ctx)

    def test_extension_update(self, mock_registry):
        data = {'name': 'new_name'}
        handler = extension.ExtensionHandler(self.ctx)
        handler.update('test_id', data)
        mock_registry.Extension.update_and_save.assert_called_once_with(
            self.ctx, 'test_id', data)

    def test_extension_create(self, mock_registry):
        data = {'name': 'new_name',
                'uuid': 'input_uuid'}
        db_obj = fakes.FakeExtension()
        mock_registry.Extension.return_value = db_obj
        handler = extension.ExtensionHandler(self.ctx)
        res = handler.create(data)
        db_obj.update.assert_called_once_with(data)
        db_obj.create.assert_called_once_with(self.ctx)
        self.assertEqual(db_obj, res)

    def test_extension_delete(self, mock_registry):
        db_obj = fakes.FakeExtension()
        mock_registry.Extension.get_by_uuid.return_value = db_obj
        handler = extension.ExtensionHandler(self.ctx)
        handler.delete('test_id')
        db_obj.destroy.assert_called_once_with(self.ctx)
        mock_registry.Extension.get_by_uuid.assert_called_once_with(self.ctx,
                                                                    'test_id')
