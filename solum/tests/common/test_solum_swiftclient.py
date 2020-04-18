# Copyright 2015 - Rackspace Hosting
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

from solum.common import exception as exc
from solum.common import solum_swiftclient as swiftclient
from solum.tests import base
from solum.tests import utils


class SwiftClientTest(base.BaseTestCase):
    """Test cases for solum.common.solum_swiftclient."""

    @mock.patch('builtins.open')
    @mock.patch('solum.common.solum_swiftclient.SwiftClient._get_swift_client')
    @mock.patch('solum.common.solum_swiftclient.SwiftClient._get_file_size')
    def test_swift_client_upload(self, mock_file_size, mock_swift_client,
                                 mock_open):

        ctxt = utils.dummy_context()
        container = 'fake-container'
        filename = 'fake-file'
        mock_client = mock_swift_client.return_value
        fsize = 5
        mock_file_size.return_value = fsize

        swift = swiftclient.SwiftClient(ctxt)
        swift.upload('filepath', container, filename)
        mock_client.put_container.assert_called_once_with(container)
        mock_client.put_object.assert_called_once_with(container,
                                                       filename,
                                                       mock.ANY,
                                                       content_length=fsize)

    @mock.patch('builtins.open')
    @mock.patch('solum.common.solum_swiftclient.SwiftClient._get_swift_client')
    @mock.patch('solum.common.solum_swiftclient.SwiftClient._get_file_size')
    def test_swift_client_upload_exception(self, mock_file_size,
                                           mock_swift_client, mock_open):

        ctxt = utils.dummy_context()
        mock_file_size.return_value = 0

        swift = swiftclient.SwiftClient(ctxt)
        self.assertRaises(exc.InvalidObjectSizeError,
                          swift.upload, 'filepath', 'fake-container', 'fname')
