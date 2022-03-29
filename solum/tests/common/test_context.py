# Copyright 2014 - Mirantis Inc.
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

from oslo_config import fixture as config

from solum.common import context
from solum.tests import base


class TestContext(base.BaseTestCase):
    def setUp(self):
        super(TestContext, self).setUp()
        self.CONF = self.useFixture(config.Config())

    def test_context_to_dict(self):
        ctx = context.RequestContext(auth_token='_token_',
                                     user='_user_',
                                     project_id='_project_id_',
                                     domain='_domain_',
                                     user_domain='_user_domain_',
                                     project_domain='_project_domain_',
                                     is_admin=False,
                                     read_only=False,
                                     request_id='_request_id_',
                                     user_name='_user_name_',
                                     roles=['admin', 'member'],
                                     auth_url='fake_auth_url',
                                     auth_token_info='_auth_token_info_',
                                     trust_id='fake_trust_id')
        ctx_dict = ctx.to_dict()
        self.assertEqual(ctx_dict['auth_token'], '_token_')
        self.assertEqual(ctx_dict['user'], '_user_')
        self.assertEqual(ctx_dict['project_id'], '_project_id_')
        self.assertEqual(ctx_dict['domain'], '_domain_')
        self.assertEqual(ctx_dict['user_domain'], '_user_domain_')
        self.assertEqual(ctx_dict['project_domain'], '_project_domain_')
        self.assertEqual(ctx_dict['is_admin'], False)
        self.assertEqual(ctx_dict['read_only'], False)
        self.assertEqual(ctx_dict['show_deleted'], False)
        self.assertEqual(ctx_dict['auth_token'], '_token_')
        self.assertIsNone(ctx_dict['resource_uuid'])
        self.assertEqual(ctx_dict['user_name'], '_user_name_')
        self.assertEqual(ctx_dict['roles'], ['admin', 'member'])
        self.assertEqual(ctx_dict['auth_url'], 'fake_auth_url')
        self.assertEqual(ctx_dict['auth_token_info'], '_auth_token_info_')
        self.assertEqual(ctx_dict['trust_id'], 'fake_trust_id')

    def test_glabal_admin_true(self):
        self.CONF.config(solum_admin_tenant_id='fake_tenant_id')
        ctx = context.RequestContext(auth_token='_token_',
                                     user='_user_',
                                     project_id='fake_tenant_id',
                                     domain='_domain_',
                                     user_domain='_user_domain_',
                                     project_domain='_project_domain_',
                                     is_admin=False,
                                     read_only=False,
                                     request_id='_request_id_',
                                     user_name='_user_name_',
                                     roles=['admin', 'member'],
                                     auth_url='fake_auth_url',
                                     auth_token_info='_auth_token_info_',
                                     trust_id='fake_trust_id')
        ctx_dict = ctx.to_dict()
        self.assertEqual(ctx_dict['auth_token'], '_token_')
        self.assertEqual(ctx_dict['user'], '_user_')
        self.assertEqual(ctx_dict['project_id'], 'fake_tenant_id')
        self.assertEqual(ctx_dict['domain'], '_domain_')
        self.assertEqual(ctx_dict['user_domain'], '_user_domain_')
        self.assertEqual(ctx_dict['project_domain'], '_project_domain_')
        self.assertEqual(ctx_dict['is_admin'], True)
        self.assertEqual(ctx_dict['read_only'], False)
        self.assertEqual(ctx_dict['show_deleted'], False)
        self.assertEqual(ctx_dict['auth_token'], '_token_')
        self.assertIsNone(ctx_dict['resource_uuid'])
        self.assertEqual(ctx_dict['user_name'], '_user_name_')
        self.assertEqual(ctx_dict['roles'], ['admin', 'member'])
        self.assertEqual(ctx_dict['auth_url'], 'fake_auth_url')
        self.assertEqual(ctx_dict['trust_id'], 'fake_trust_id')

    def test_global_admin_false(self):
        self.CONF.config(solum_admin_tenant_id='fake_tenant_id')
        ctx = context.RequestContext(auth_token='_token_',
                                     user='_user_',
                                     project_id='_tenant_id_',
                                     domain='_domain_',
                                     user_domain='_user_domain_',
                                     project_domain='_project_domain_',
                                     is_admin=False,
                                     read_only=False,
                                     request_id='_request_id_',
                                     user_name='_user_name_',
                                     roles=['admin', 'member'],
                                     auth_url='fake_auth_url',
                                     auth_token_info='_auth_token_info_',
                                     trust_id='fake_trust_id')
        ctx_dict = ctx.to_dict()
        self.assertEqual(ctx_dict['auth_token'], '_token_')
        self.assertEqual(ctx_dict['user'], '_user_')
        self.assertEqual(ctx_dict['project_id'], '_tenant_id_')
        self.assertEqual(ctx_dict['domain'], '_domain_')
        self.assertEqual(ctx_dict['user_domain'], '_user_domain_')
        self.assertEqual(ctx_dict['project_domain'], '_project_domain_')
        self.assertEqual(ctx_dict['is_admin'], False)
        self.assertEqual(ctx_dict['read_only'], False)
        self.assertEqual(ctx_dict['show_deleted'], False)
        self.assertEqual(ctx_dict['auth_token'], '_token_')
        self.assertIsNone(ctx_dict['resource_uuid'])
        self.assertEqual(ctx_dict['user_name'], '_user_name_')
        self.assertEqual(ctx_dict['roles'], ['admin', 'member'])
        self.assertEqual(ctx_dict['auth_url'], 'fake_auth_url')
        self.assertEqual(ctx_dict['trust_id'], 'fake_trust_id')
