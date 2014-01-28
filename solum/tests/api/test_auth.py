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

from solum.api import auth
from solum.openstack.common.fixture import config
from solum.tests import base
from solum.tests import fakes


class TestAuth(base.BaseTestCase):

    def setUp(self):
        super(TestAuth, self).setUp()
        self.CONF = self.useFixture(config.Config())
        self.app = fakes.FakeApp()

    def test_check_auth_option_enabled(self):

        self.CONF.config(auth_protocol="footp",
                         auth_version="v2.0",
                         auth_uri=None,
                         group=auth.OPT_GROUP_NAME)
        with mock.patch('keystoneclient.middleware.auth_token.AuthProtocol',
                        new_callable=fakes.FakeAuthProtocol):
            self.CONF.config(enable_authentication='True')
            result = auth.install(self.app, self.CONF.conf)
            self.assertIsInstance(result, fakes.FakeAuthProtocol)

    def test_check_auth_option_disabled(self):
        self.CONF.config(auth_protocol="footp",
                         auth_version="v2.0",
                         auth_uri=None,
                         group=auth.OPT_GROUP_NAME)
        with mock.patch('keystoneclient.middleware.auth_token.AuthProtocol',
                        new_callable=fakes.FakeAuthProtocol):
            self.CONF.config(enable_authentication='False')
            result = auth.install(self.app, self.CONF.conf)
            self.assertIsInstance(result, fakes.FakeApp)
