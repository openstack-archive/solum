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
            "publicURL": "http://nova.publicinternets.com/v1.0/"}


class TestTraceData(base.BaseTestCase):
    def test_context_to_dict(self):
        ctx = context.RequestContext('_token_', '_user_', '_tenant_',
                                     '_domain_', '_user_domain_',
                                     '_project_domain_', False, False,
                                     '_request_id_', '_user_name_',
                                     ['admin', 'member'],
                                     [{'endpoints': [endpoint],
                                       "endpoints_links": [],
                                       "type": "compute",
                                       "name": "nova"}])
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
        self.assertEqual(ctx_dict['service_catalog'],
                         [{'endpoints': [endpoint],
                           "endpoints_links": [],
                           "type": "compute",
                           "name": "nova"}])
