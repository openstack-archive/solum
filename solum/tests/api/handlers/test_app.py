# Copyright (c) 2015 Rackspace Hosting
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


from solum.api.handlers import app_handler
from solum.common import exception as exc
from solum import objects
from solum.tests import base
from solum.tests import fakes
from solum.tests import utils


@mock.patch('solum.objects.registry')
class TestAppHandler(base.BaseTestCase):
    def setUp(self):
        super(TestAppHandler, self).setUp()
        self.ctx = utils.dummy_context()

    def test_app_get(self, mock_registry):
        mock_registry.App.get_by_uuid.return_value = {}
        handler = app_handler.AppHandler(self.ctx)
        res = handler.get('test_id')
        self.assertIsNotNone(res)
        get_by_uuid = mock_registry.App.get_by_uuid
        get_by_uuid.assert_called_once_with(self.ctx, 'test_id')

    def test_app_get_all(self, mock_registry):
        mock_registry.App.get_all.return_value = {}
        handler = app_handler.AppHandler(self.ctx)
        res = handler.get_all()
        self.assertIsNotNone(res)
        mock_registry.AppList.get_all.assert_called_once_with(self.ctx)

    @mock.patch('solum.deployer.api.API.destroy_app')
    def test_app_delete(self, mock_destroy, mock_registry):
        handler = app_handler.AppHandler(self.ctx)
        handler.delete('test_id')
        mock_destroy.assert_called_once_with('test_id')

    @mock.patch('solum.common.clients.OpenStackClients.keystone')
    def test_app_create(self, mock_kc, mock_registry):
        data = {'name': 'fakeapp',
                'description': 'fake app for testing',
                'source': {
                    'repository': 'https://github.com/example/a.git',
                    'revision': 'master'
                }}
        raw_content = {'a': 'b'}
        data['raw_content'] = json.dumps(raw_content)
        self.ctx.password = 'password'
        db_obj = fakes.FakeApp()
        mock_registry.App.return_value = db_obj
        handler = app_handler.AppHandler(self.ctx)
        res = handler.create(data)
        db_obj.create.assert_called_once_with(self.ctx)
        self.assertEqual(db_obj, res)

    @mock.patch('solum.common.clients.OpenStackClients.keystone')
    def test_app_create_invalid_repo_url(self, mock_kc, mock_registry):
        invalid_urls_list = list()
        invalid_urls_list.append('http://github.com/skdhfskjhdks')
        invalid_urls_list.append('github.com/abc/xyz')
        invalid_urls_list.append('xyz://github.com/abc/xyz.git')
        invalid_urls_list.append('xyz://github.com/abc/xyz')
        invalid_urls_list.append('abc')
        invalid_urls_list.append('http')
        invalid_urls_list.append('git')

        for invalid_url in invalid_urls_list:
            data = {'name': 'fakeapp',
                    'description': 'fake app for testing',
                    'source': {
                        'repository': invalid_url,
                        'revision': 'master'
                    }}
            raw_content = {'a': 'b'}
            data['raw_content'] = json.dumps(raw_content)
            self.ctx.password = 'password'

            db_obj = fakes.FakeApp()
            mock_registry.App.return_value = db_obj
            handler = app_handler.AppHandler(self.ctx)

            self.assertRaises(exc.BadRequest, handler.create, data)
            assert not db_obj.create.called, 'db_obj.create called'

    def test_app_patch(self, mock_registry):
        mock_registry.App.side_effect = [mock.MagicMock(), mock.MagicMock()]
        db_obj = objects.registry.App()
        # Without this, I'd just get a mocked function call.
        # I want real data so I can track that it's being updated.
        a = fakes.FakeApp().as_dict()
        db_obj.as_dict.return_value = a
        mock_registry.App.get_by_uuid.return_value = db_obj
        # I'm not saving anything anyway, I just want to make sure
        # that I'm sending the right data to update_and_save.
        mock_registry.App.update_and_save = (
            lambda context, obj_id, data_dict: data_dict)

        # Build a phony app whose as_dict returns this dict below.
        to_update_data = {
            'name': 'newfakeapp',
            'workflow_config': {
                'run_cmd': 'newruncommand',
            },
            'source': {
                'revision': 'experimental',
            },
            'repo_token': 'abc'
        }
        handler = app_handler.AppHandler(self.ctx)
        new_app = objects.registry.App()
        new_app.as_dict.return_value = to_update_data

        # The actual call to handler.patch
        updated = handler.patch('test_id', new_app)

        self.assertEqual('newfakeapp', updated['name'])
        self.assertEqual('newruncommand',
                         updated['workflow_config']['run_cmd'])
        self.assertEqual('python ./tests.py',
                         updated['workflow_config']['test_cmd'])
        self.assertEqual('http://github.com/example/a.git',
                         updated['source']['repository'])
        self.assertEqual('experimental',
                         updated['source']['revision'])
