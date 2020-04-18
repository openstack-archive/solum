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

from oslo_config import cfg

from solum.tests import base
from solum.tests import fakes
from solum.tests import utils
import solum.uploaders.swift as uploader


class SwiftUploadTest(base.BaseTestCase):
    def setUp(self):
        super(SwiftUploadTest, self).setUp()

    @mock.patch('builtins.open')
    @mock.patch('solum.uploaders.swift.SwiftUpload._upload')
    @mock.patch('solum.uploaders.common.UploaderBase.transform_jsonlog')
    @mock.patch('solum.uploaders.common.UploaderBase.write_userlog_row')
    def test_upload_on_assembly_delete(self, mock_write_row, mock_trans_jlog,
                                       mock_upload, mock_open):
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
                                        build_id,
                                        stage, build_id)

        self.assertTrue(mock_trans_jlog.called)
        tansf_path = orig_path + '.tf'
        mock_upload.assert_called_once_with(container, filename, tansf_path)
        mock_write_row.assert_called_once_with(filename, swift_info)

    @mock.patch('builtins.open')
    @mock.patch('solum.common.solum_swiftclient.SwiftClient.upload')
    @mock.patch('solum.uploaders.common.UploaderBase.transform_jsonlog')
    @mock.patch('solum.uploaders.common.UploaderBase.write_userlog_row')
    def test_upload(self, mock_write_row, mock_trans_jlog, mock_swift,
                    mock_open):
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
        resource = swiftupload.resource

        swiftupload.upload_log()

        swift_info = {'container': container}

        filename = "%s-%s/%s-%s.log" % (resource.name,
                                        build_id,
                                        stage, build_id)

        self.assertTrue(mock_trans_jlog.called)
        tansf_path = orig_path + '.tf'
        mock_swift.assert_called_once_with(tansf_path,
                                           container,
                                           filename)
        mock_write_row.assert_called_once_with(filename, swift_info)
