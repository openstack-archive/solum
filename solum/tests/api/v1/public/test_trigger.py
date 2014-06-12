# Copyright 2013 - Red Hat, Inc.
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

from solum.api.controllers.v1.pub import trigger
from solum.common import exception
from solum.tests import base
from solum.tests import fakes


@mock.patch('pecan.request', new_callable=fakes.FakePecanRequest)
@mock.patch('pecan.response', new_callable=fakes.FakePecanResponse)
@mock.patch('solum.api.controllers.v1.pub.trigger.assembly_handler'
            '.AssemblyHandler')
class TestTriggerController(base.BaseTestCase):
    def test_trigger_post(self, handler_mock, resp_mock, request_mock):
        obj = trigger.TriggerController()
        obj.post('test_id')
        self.assertEqual(202, resp_mock.status)
        tw = handler_mock.return_value.trigger_workflow
        tw.assert_called_once_with('test_id')

    def test_trigger_post_error(self, handler_mock, resp_mock, request_mock):
        obj = trigger.TriggerController()
        handler_mock.return_value.trigger_workflow.side_effect = (
            exception.ResourceNotFound(name='trigger', id='test_id'))
        obj.post('test_id')
        self.assertEqual(404, resp_mock.status)
        tw = handler_mock.return_value.trigger_workflow
        tw.assert_called_once_with('test_id')
