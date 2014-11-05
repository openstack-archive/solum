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

from solum.tests import base
from solum.tests import fakes
from solum.tests import utils
import solum.uploaders.swift as uploader


class SwiftUploadTest(base.BaseTestCase):
    def setUp(self):
        super(SwiftUploadTest, self).setUp()

    @mock.patch('open')
    @mock.patch('clients.OpenStackClients')
    @mock.patch('oslo.config.cfg.CONF.worker')
    def test_upload(self, mock_config, mock_client, mock_open):
        ctxt = utils.dummy_context()
        orig_path = "original path"
        assembly = fakes.FakeAssembly()
        build_id = "5678"
        container = 'fake-container'
        mock_config.log_upload_swift_container.return_value = container
        mock_swift = mock.MagicMock()
        mock_client.return_value.swift.return_value = mock_swift
        fake_file = mock.MagicMock()
        mock_open.return_value = fake_file
        swiftupload = uploader.SwiftUpload(ctxt, orig_path,
                                           assembly, build_id,
                                           "fakestage")
        swiftupload.transform_jsonlog = mock.MagicMock()
        swiftupload.write_userlog_row = mock.MagicMock()
        swiftupload.upload()
        swift_info = {'container': container}

        swiftupload.write_userlog_row.assert_called_once_with(orig_path,
                                                              swift_info)
        swiftupload.transform_jsonlog.assert_called_once()
        mock_swift.put_container.assert_called_once_with(container)
        mock_swift.put_object.assembly_id(container, orig_path, fake_file)
