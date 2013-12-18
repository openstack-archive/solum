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

'''Keystone client import fails in python3.
Per conversation with Keystone team they
will fix this in a new keystoneclient release.
Keystone Bug #1261572
https://bugs.launchpad.net/keystone/+bug/1261572
'''

failed_import = False
try:
    from solum.api import app as api_app
except Exception:
    failed_import = True

from solum.api import config as api_config
from solum.tests import base


class TestAppConfig(base.BaseTestCase):
    def setUp(self):
        super(TestAppConfig, self).setUp()
        if failed_import:
            self.skipTest('Not all modules were imported.')

    def test_get_pecan_config(self):
        config = api_app.get_pecan_config()

        config_d = dict(config.app)

        self.assertEqual(config_d, api_config.app)
