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

from unittest import mock

from oslo_config import fixture as config

from solum.api import auth
from solum.common import context
from solum.tests import base
from solum.tests import fakes


@mock.patch('solum.api.auth.AuthProtocolWrapper',
            new_callable=fakes.FakeAuthProtocol)
class TestAuth(base.BaseTestCase):

    def setUp(self):
        super(TestAuth, self).setUp()
        self.CONF = self.useFixture(config.Config())
        self.app = fakes.FakeApp()

    def test_check_auth_option_enabled(self, mock_auth):

        self.CONF.config(auth_protocol="http",
                         auth_version="v2.0",
                         www_authenticate_uri=None,
                         group=auth.OPT_GROUP_NAME)
        self.CONF.config(enable_authentication=True)
        result = auth.install(self.app, self.CONF.conf)
        self.assertIsInstance(result, fakes.FakeAuthProtocol)

    def test_check_auth_option_disabled(self, mock_auth):
        self.CONF.config(auth_protocol="http",
                         auth_version="v2.0",
                         www_authenticate_uri=None,
                         group=auth.OPT_GROUP_NAME)
        self.CONF.config(enable_authentication=False)
        result = auth.install(self.app, self.CONF.conf)
        self.assertIsInstance(result, fakes.FakeApp)

    def test_auth_hook_before_method(self, mock_cls):
        state = mock.Mock(request=fakes.FakePecanRequest())
        hook = auth.ContextHook()
        hook.before(state)
        ctx = state.request.security_context
        self.assertIsInstance(ctx, context.RequestContext)
        self.assertEqual(ctx.auth_token,
                         fakes.fakeAuthTokenHeaders['X-Auth-Token'])
        self.assertEqual(ctx.tenant,
                         fakes.fakeAuthTokenHeaders['X-Project-Id'])
        self.assertEqual(ctx.user,
                         fakes.fakeAuthTokenHeaders['X-User-Id'])
        self.assertEqual(ctx.roles,
                         [u'admin', u'ResellerAdmin', u'_member_'])
        self.assertEqual(ctx.user_name,
                         fakes.fakeAuthTokenHeaders['X-User-Name'])
        self.assertEqual(ctx.domain,
                         fakes.fakeAuthTokenHeaders['X-Domain-Name'])
        self.assertEqual(ctx.project_domain,
                         fakes.fakeAuthTokenHeaders['X-Project-Domain-Id'])
        self.assertEqual(ctx.user_domain,
                         fakes.fakeAuthTokenHeaders['X-User-Domain-Id'])
        self.assertIsNone(ctx.auth_token_info)

    def test_auth_hook_before_method_auth_info(self, mock_cls):
        state = mock.Mock(request=fakes.FakePecanRequest())
        state.request.environ['keystone.token_info'] = 'assert_this'
        hook = auth.ContextHook()
        hook.before(state)
        ctx = state.request.security_context
        self.assertIsInstance(ctx, context.RequestContext)
        self.assertEqual(fakes.fakeAuthTokenHeaders['X-Auth-Token'],
                         ctx.auth_token)
        self.assertEqual('assert_this', ctx.auth_token_info)
