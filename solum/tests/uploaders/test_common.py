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

from solum.tests import base
from solum.tests import fakes
from solum.tests import utils
from solum.uploaders import common as uploader


class CommonTest(base.BaseTestCase):
    def setUp(self):
        super(CommonTest, self).setUp()

    def test_upload(self):
        ctxt = utils.dummy_context()
        orig_path = "original path"
        assembly = fakes.FakeAssembly()
        build_id = "5678"

        baseuploader = uploader.UploaderBase(ctxt, orig_path,
                                             assembly, build_id,
                                             "fakestage")

        baseuploader.write_userlog_row = mock.MagicMock()

        baseuploader.upload_log()

        self.assertEqual(0, baseuploader.write_userlog_row.call_count)
