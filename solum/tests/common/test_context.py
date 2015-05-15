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

from solum.common import context
from solum.openstack.common.fixture import config
from solum.tests import base


class TestContext(base.BaseTestCase):
    def setUp(self):
        super(TestContext, self).setUp()
        self.CONF = self.useFixture(config.Config())

    def test_context_to_dict(self):
        ctx = context.RequestContext('_token_', '_user_', '_tenant_',
                                     '_domain_', '_user_domain_',
                                     '_project_domain_', False, False,
                                     '_request_id_', '_user_name_',
                                     ['admin', 'member'], 'fake_auth_url',
                                     trust_id='fake_trust_id')
        ctx_dict = ctx.to_dict()
        self.assertEqual(ctx_dict['auth_token'], '_token_')
        self.assertEqual(ctx_dict['user'], '_user_')
        self.assertEqual(ctx_dict['tenant'], '_tenant_')
        self.assertEqual(ctx_dict['domain'], '_domain_')
        self.assertEqual(ctx_dict['user_domain'], '_user_domain_')
        self.assertEqual(ctx_dict['project_domain'], '_project_domain_')
        self.assertEqual(ctx_dict['is_admin'], False)
        self.assertEqual(ctx_dict['read_only'], False)
        self.assertEqual(ctx_dict['show_deleted'], False)
        self.assertEqual(ctx_dict['auth_token'], '_token_')
        self.assertEqual(ctx_dict['instance_uuid'], None)
        self.assertEqual(ctx_dict['user_name'], '_user_name_')
        self.assertEqual(ctx_dict['roles'], ['admin', 'member'])
        self.assertEqual(ctx_dict['auth_url'], 'fake_auth_url')
        self.assertEqual(ctx_dict['trust_id'], 'fake_trust_id')

    def test_glabal_admin_true(self):
        self.CONF.config(solum_admin_tenant_id='fake_tenant_id')
        ctx = context.RequestContext('_token_', '_user_', 'fake_tenant_id',
                                     '_domain_', '_user_domain_',
                                     '_project_domain_', False, False,
                                     '_request_id_', '_user_name_',
                                     ['admin', 'member'], 'fake_auth_url',
                                     trust_id='fake_trust_id')
        ctx_dict = ctx.to_dict()
        self.assertEqual(ctx_dict['auth_token'], '_token_')
        self.assertEqual(ctx_dict['user'], '_user_')
        self.assertEqual(ctx_dict['tenant'], 'fake_tenant_id')
        self.assertEqual(ctx_dict['domain'], '_domain_')
        self.assertEqual(ctx_dict['user_domain'], '_user_domain_')
        self.assertEqual(ctx_dict['project_domain'], '_project_domain_')
        self.assertEqual(ctx_dict['is_admin'], True)
        self.assertEqual(ctx_dict['read_only'], False)
        self.assertEqual(ctx_dict['show_deleted'], False)
        self.assertEqual(ctx_dict['auth_token'], '_token_')
        self.assertEqual(ctx_dict['instance_uuid'], None)
        self.assertEqual(ctx_dict['user_name'], '_user_name_')
        self.assertEqual(ctx_dict['roles'], ['admin', 'member'])
        self.assertEqual(ctx_dict['auth_url'], 'fake_auth_url')
        self.assertEqual(ctx_dict['trust_id'], 'fake_trust_id')

    def test_glabal_admin_false(self):
        self.CONF.config(solum_admin_tenant_id='fake_tenant_id')
        ctx = context.RequestContext('_token_', '_user_', '_tenant_id_',
                                     '_domain_', '_user_domain_',
                                     '_project_domain_', False, False,
                                     '_request_id_', '_user_name_',
                                     ['admin', 'member'], 'fake_auth_url',
                                     trust_id='fake_trust_id')
        ctx_dict = ctx.to_dict()
        self.assertEqual(ctx_dict['auth_token'], '_token_')
        self.assertEqual(ctx_dict['user'], '_user_')
        self.assertEqual(ctx_dict['tenant'], '_tenant_id_')
        self.assertEqual(ctx_dict['domain'], '_domain_')
        self.assertEqual(ctx_dict['user_domain'], '_user_domain_')
        self.assertEqual(ctx_dict['project_domain'], '_project_domain_')
        self.assertEqual(ctx_dict['is_admin'], False)
        self.assertEqual(ctx_dict['read_only'], False)
        self.assertEqual(ctx_dict['show_deleted'], False)
        self.assertEqual(ctx_dict['auth_token'], '_token_')
        self.assertEqual(ctx_dict['instance_uuid'], None)
        self.assertEqual(ctx_dict['user_name'], '_user_name_')
        self.assertEqual(ctx_dict['roles'], ['admin', 'member'])
        self.assertEqual(ctx_dict['auth_url'], 'fake_auth_url')
        self.assertEqual(ctx_dict['trust_id'], 'fake_trust_id')
