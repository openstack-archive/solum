# Copyright 2014 - Rackspace Hosting
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

import mock

from solum.api.controllers.v1 import userlog
from solum import objects
from solum.tests import base
from solum.tests import fakes


@mock.patch('pecan.request', new_callable=fakes.FakePecanRequest)
@mock.patch('pecan.response', new_callable=fakes.FakePecanResponse)
@mock.patch('solum.api.handlers.userlog_handler.UserlogHandler')
class TestUserlogsController(base.BaseTestCase):
    def setUp(self):
        super(TestUserlogsController, self).setUp()
        objects.load()

    def test_userlogs_get_all(self, UserlogHandler,
                              resp_mock, request_mock):
        hand_get = UserlogHandler.return_value.get_all_by_assembly_id
        fake_userlog = fakes.FakeUserlog()
        assembly_id = fake_userlog.assembly_uuid
        hand_get.return_value = [fake_userlog]
        resp = userlog.UserlogsController(assembly_id).get_all()
        self.assertEqual(fake_userlog.assembly_uuid,
                         resp['result'][0].assembly_uuid)
        self.assertEqual(fake_userlog.location, resp['result'][0].location)
        self.assertEqual(fake_userlog.strategy, resp['result'][0].strategy)
        self.assertEqual(fake_userlog.strategy_info,
                         resp['result'][0].strategy_info)
        hand_get.assert_called_with(assembly_id)
        self.assertEqual(200, resp_mock.status)
        self.assertIsNotNone(resp)
