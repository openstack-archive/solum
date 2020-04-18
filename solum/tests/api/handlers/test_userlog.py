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


from solum.api.handlers import userlog_handler
from solum.tests import base
from solum.tests import fakes
from solum.tests import utils


@mock.patch('solum.objects.registry')
class TestUserlogHandler(base.BaseTestCase):
    def setUp(self):
        super(TestUserlogHandler, self).setUp()
        self.ctx = utils.dummy_context()

    def test_userlog_get_all(self, mock_registry):
        mock_registry.UserlogList.get_all.return_value = {}
        handler = userlog_handler.UserlogHandler(self.ctx)
        res = handler.get_all()
        self.assertIsNotNone(res)
        mock_registry.UserlogList.get_all.assert_called_once_with(self.ctx)

    def test_userlog_get_all_by_id(self, mock_registry):
        mock_registry.UserlogList.get_all_by_id.return_value = {}
        handler = userlog_handler.UserlogHandler(self.ctx)
        assembly = fakes.FakeAssembly()
        res = handler.get_all_by_id(assembly.id)
        self.assertIsNotNone(res)
        all_by_id = mock_registry.UserlogList.get_all_by_id
        all_by_id.assert_called_once_with(self.ctx, resource_uuid=assembly.id)

    @mock.patch('solum.api.handlers.userlog_handler.os.remove')
    def test_userlog_delete_local_logs(self, mock_os_remove, mock_registry):
        fi = fakes.FakeImage()
        fakelog = fakes.FakeUserlog()
        flogs = [fakelog]
        mock_registry.UserlogList.get_all_by_id.return_value = flogs

        handler = userlog_handler.UserlogHandler(self.ctx)
        handler.delete(fi.uuid)

        mock_registry.UserlogList.get_all_by_id.assert_called_once_with(
            self.ctx, resource_uuid=fi.uuid)
        mock_os_remove.assert_called_once_with(flogs[0].location)
        fakelog.destroy.assert_called_once_with(self.ctx)

    @mock.patch('solum.common.solum_swiftclient.SwiftClient.delete_object')
    def test_userlog_delete_swift_logs(self, mock_swift_delete, mock_registry):
        fi = fakes.FakeImage()
        fakelog = fakes.FakeUserlog()
        fakelog.strategy = 'swift'
        fakelog.strategy_info = '{"container": "solum-logs"}'
        flogs = [fakelog]
        s_info = json.loads(flogs[0].strategy_info)['container']
        location = flogs[0].location
        mock_registry.UserlogList.get_all_by_id.return_value = flogs

        handler = userlog_handler.UserlogHandler(self.ctx)
        handler.delete(fi.uuid)

        mock_registry.UserlogList.get_all_by_id.assert_called_once_with(
            self.ctx, resource_uuid=fi.uuid)
        mock_swift_delete.assert_called_once_with(s_info, location)
        fakelog.destroy.assert_called_once_with(self.ctx)
