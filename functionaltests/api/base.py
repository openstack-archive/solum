# -*- coding: utf-8 -*-
#
# Copyright 2013 - Noorul Islam K M
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

import time

from tempest import auth
from tempest import clients
from tempest.common import http
from tempest.common import rest_client
from tempest import config
import testtools

CONF = config.CONF


class SolumClient(rest_client.RestClient):

    def __init__(self, auth_provider):
        super(SolumClient, self).__init__(auth_provider)
        self.service = 'application_deployment'
        self.endpoint_url = 'publicURL'

    def request_without_auth(self, resource, method, headers={}, body=None):
        dscv = CONF.identity.disable_ssl_certificate_validation
        http_obj = http.ClosingHttp(disable_ssl_certificate_validation=dscv)
        url = '%s/%s' % (self.base_url, resource)
        return http_obj.request(url, method, headers=headers, body=body)

    def assembly_delete_done(self, assembly_uuid):
        wait_interval = 1
        growth_factor = 1.2
        max_attempts = 5

        for count in range(max_attempts):
            try:
                resp, body = self.get('v1/assemblies/%s' % assembly_uuid)
            except Exception:
                return True
            time.sleep(wait_interval)
            wait_interval *= growth_factor

        return False


class TestCase(testtools.TestCase):
    def setUp(self):
        super(TestCase, self).setUp()

        credentials = SolumCredentials()

        mgr = clients.Manager()
        auth_provider = mgr.get_auth_provider(credentials)
        self.client = SolumClient(auth_provider)


class SolumCredentials(auth.KeystoneV2Credentials):

    def __init__(self):
        creds = dict(
            username=CONF.identity.username,
            password=CONF.identity.password,
            tenant_name=CONF.identity.tenant_name
        )

        super(SolumCredentials, self).__init__(**creds)
