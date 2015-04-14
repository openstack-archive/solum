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
from oslo.config import cfg

from solum.tests import base
from solum.tests import fakes
from solum.tests import utils
import solum.uploaders.swift as uploader


class SwiftUploadTest(base.BaseTestCase):
    def setUp(self):
        super(SwiftUploadTest, self).setUp()

    def test_upload_on_assembly_delete(self):
        ctxt = utils.dummy_context()
        orig_path = "original path"
        assembly = fakes.FakeAssembly()
        build_id = "5678"
        container = 'fake-container'

        cfg.CONF.worker.log_upload_swift_container = container

        stage = "fakestage"
        swiftupload = uploader.SwiftUpload(ctxt, orig_path,
                                           assembly, build_id,
                                           stage)
        swiftupload._open = mock.MagicMock()
        swiftupload._upload = mock.MagicMock()
        swiftupload.transform_jsonlog = mock.MagicMock()
        swiftupload.write_userlog_row = mock.MagicMock()

        rs_before_delete = swiftupload.resource
        name_before = swiftupload.resource.name
        uuid_before = swiftupload.resource.uuid

        # Delete the assembly object before calling upload_log()
        del assembly

        swiftupload.upload_log()

        self.assertEqual(name_before, swiftupload.resource.name)
        self.assertEqual(uuid_before, swiftupload.resource.uuid)

        # Asserts
        swift_info = {'container': container}

        filename = "%s-%s/%s-%s.log" % (rs_before_delete.name,
                                        rs_before_delete.uuid,
                                        stage, build_id)

        swiftupload.transform_jsonlog.assert_called_once()
        swiftupload._upload.assert_called_once()
        swiftupload.write_userlog_row.assert_called_once_with(filename,
                                                              swift_info)

    def test_upload(self):
        ctxt = utils.dummy_context()
        orig_path = "original path"
        assembly = fakes.FakeAssembly()
        build_id = "5678"
        container = 'fake-container'
        cfg.CONF.worker.log_upload_swift_container = container

        stage = "fakestage"

        swiftupload = uploader.SwiftUpload(ctxt, orig_path,
                                           assembly, build_id,
                                           stage)
        swiftupload._open = mock.MagicMock()
        swiftupload._upload = mock.MagicMock()
        swiftupload.transform_jsonlog = mock.MagicMock()
        swiftupload.write_userlog_row = mock.MagicMock()

        resource = swiftupload.resource

        swiftupload.upload_log()

        swift_info = {'container': container}

        filename = "%s-%s/%s-%s.log" % (resource.name,
                                        resource.uuid,
                                        stage, build_id)

        swiftupload.transform_jsonlog.assert_called_once()
        swiftupload._upload.assert_called_once()
        swiftupload.write_userlog_row.assert_called_once_with(filename,
                                                              swift_info)

    @mock.patch('swiftclient.client.Connection')
    def test_upload_image(self, mock_conn):

        container = "solum_du"
        name = "test_file"
        swiftupload = self._get_connection_handle(container, name)
        swiftupload._open = mock.MagicMock()
        swiftupload._upload = mock.MagicMock()

        swiftupload.upload_image()
        swiftupload._upload.assert_called_once()

    @mock.patch('swiftclient.client.Connection')
    def test_stat(self, mock_conn):
        swift_client = self._get_connection_handle('', '')
        swift_client.stat()

    def _get_connection_handle(self, container, name):
        client_args = {"region_name": "RegionOne",
                       "auth_token": "token123",
                       "storage_url": "http://storehere",
                       "container": container,
                       "name": name,
                       "path": "http://path123"}
        swiftupload = uploader.SwiftUpload(**client_args)
        return swiftupload
