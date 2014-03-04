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

import json

from solum.common import context
from solum.tests import base

'''Keystone Auth Middleware returns a Service Catalog as an array of
endpoints. The example below represents the actual format of the endpoint'''

endpoint = {"internalURL": "http://localhost:8774/v1.0",
            "name": "nova_compat",
            "adminURL": "http://127.0.0.1:8774/v1.0",
            "region": "RegionOne",
            "tenantId": 1,
            "type": "compute",
            "id": 2,
            "publicURL": "http://nova.example.com/v1.0/"}
ks_endpoint = {"internalURL": "http://127.0.0.1:5000/v2.0",
               "name": "keystone",
               "adminURL": "http://keystone.example.com:35357/v2.0",
               "region": "RegionOne",
               "tenantId": 1,
               "type": "identity",
               "id": 1,
               "publicURL": "http://keystone.example.com:5000/v2.0/"}


class TestContext(base.BaseTestCase):
    def setUp(self):
        super(TestContext, self).setUp()
        self.catalog = json.dumps([{'endpoints': [endpoint],
                                    "endpoints_links": [],
                                    "type": "compute",
                                    "name": "nova"},
                                   {'endpoints': [ks_endpoint],
                                    "endpoints_links": [],
                                    "type": "identity",
                                    "name": "keystone"}])

    def test_context_to_dict(self):
        ctx = context.RequestContext('_token_', '_user_', '_tenant_',
                                     '_domain_', '_user_domain_',
                                     '_project_domain_', False, False,
                                     '_request_id_', '_user_name_',
                                     ['admin', 'member'],
                                     self.catalog)
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
        self.assertEqual(self.catalog, ctx_dict['service_catalog'])

    def test_context_url_for(self):
        ctx = context.RequestContext('_token_', '_user_', '_tenant_',
                                     '_domain_', '_user_domain_',
                                     '_project_domain_', False, False,
                                     '_request_id_', '_user_name_',
                                     ['admin', 'member'],
                                     self.catalog)

        url = ctx.get_url_for(service_type='compute',
                              endpoint_type='publicURL')
        self.assertEqual("http://nova.example.com/v1.0/", url)
        url = ctx.get_url_for(service_type='compute',
                              endpoint_type='internalURL')
        self.assertEqual("http://localhost:8774/v1.0", url)

    def test_context_auth_url(self):
        ctx = context.RequestContext('_token_', '_user_', '_tenant_',
                                     '_domain_', '_user_domain_',
                                     '_project_domain_', False, False,
                                     '_request_id_', '_user_name_',
                                     ['admin', 'member'],
                                     self.catalog)

        url = ctx.auth_url
        self.assertEqual("http://keystone.example.com:5000/v2.0/", url)
