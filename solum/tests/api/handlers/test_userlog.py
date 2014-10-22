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

import mock

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

    def test_userlog_get_all_by_assembly_id(self, mock_registry):
        mock_registry.UserlogList.get_all_by_assembly_id.return_value = {}
        handler = userlog_handler.UserlogHandler(self.ctx)
        assembly = fakes.FakeAssembly()
        res = handler.get_all_by_assembly_id(assembly.id)
        self.assertIsNotNone(res)
        all_by_id = mock_registry.UserlogList.get_all_by_assembly_id
        all_by_id.assert_called_once_with(self.ctx, assembly_uuid=assembly.id)
