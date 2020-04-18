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

from unittest import mock

from solum.common.rpc import service
from solum.tests import base


class ServiceTest(base.BaseTestCase):

    def test_create(self):
        topic, server, handlers = 'fake_topic', 'fake_host', []
        rpc_service = service.Service(topic, server, handlers)
        self.assertIsNotNone(rpc_service._server)


class APITest(base.BaseTestCase):

    def test_create(self):
        topic = 'fake_topic'
        rpc_api = service.API(context={}, topic=topic)
        self.assertIsNotNone(rpc_api._client)

    def test_cast(self):
        topic = 'fake_topic'
        rpc_api = service.API(context={}, topic=topic)
        rpc_api._cast = mock.MagicMock()
        rpc_api.echo('foo')
        rpc_api._cast.assert_called_once_with('echo', message='foo')
