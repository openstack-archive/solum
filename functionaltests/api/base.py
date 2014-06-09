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

import copy
import json
import os
import time

from tempest import auth
from tempest import clients
from tempest.common import http
from tempest.common import rest_client
from tempest import config
import testtools
import yaml

CONF = config.CONF

assembly_sample_data = {"name": "test_assembly",
                        "description": "A test to create assembly",
                        "project_id": "project_id",
                        "user_id": "user_id",
                        "status": "status",
                        "application_uri": "http://localhost:5000"}

plan_sample_data = {"version": "1",
                    "name": "test_plan",
                    "description": "A test to create plan",
                    "project_id": "project_id",
                    "user_id": "user_id",
                    "artifacts": [{
                        "name": "No deus",
                        "artifact_type": "heroku",
                        "content": {
                            "href": "https://example.com/git/a.git",
                            "private": False
                        },
                        "language_pack": "auto",
                        }]}


class SolumClient(rest_client.RestClient):

    def __init__(self, auth_provider):
        super(SolumClient, self).__init__(auth_provider)
        self.service = 'application_deployment'
        self.endpoint_url = 'publicURL'
        self.created_assemblies = []
        self.created_plans = []

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

    def create_assembly(self, plan_uuid, data=None):
        assembly_data = copy.deepcopy(data or assembly_sample_data)
        assembly_data['plan_uri'] = "%s/v1/plans/%s" % (self.base_url,
                                                        plan_uuid)
        jsondata = json.dumps(assembly_data)
        resp, body = self.post('v1/assemblies', jsondata)
        assembly_resp = SolumResponse(resp=resp, body=body, body_type='json')
        uuid = assembly_resp.uuid
        if uuid is not None:
            self.created_assemblies.append(uuid)
        return assembly_resp

    def create_plan(self, data=None):
        plan_data = copy.deepcopy(data or plan_sample_data)
        yaml_data = yaml.dump(plan_data)
        resp, body = self.post('v1/plans', yaml_data,
                               headers={'content-type': 'application/x-yaml'})
        plan_resp = SolumResponse(resp=resp, body=body, body_type='yaml')
        uuid = plan_resp.uuid
        if uuid is not None:
            self.created_plans.append(uuid)
        return plan_resp

    def delete_created_assemblies(self):
        [self.delete_assembly(uuid) for uuid in list(self.created_assemblies)]
        self.created_assemblies = []

    def delete_assembly(self, uuid):
        resp, body = self.delete('v1/assemblies/%s' % uuid)
        if self.assembly_delete_done(uuid):
            self.created_assemblies.remove(uuid)
        return resp, body

    def delete_created_plans(self):
        self.delete_created_assemblies()
        [self.delete_plan(uuid) for uuid in list(self.created_plans)]
        self.created_plans = []

    def delete_plan(self, uuid):
        resp, body = self.delete(
            'v1/plans/%s' % uuid,
            headers={'content-type': 'application/x-yaml'})
        self.created_plans.remove(uuid)
        return resp, body


class SolumResponse():
    def __init__(self, resp, body, body_type):
        self.resp = resp
        self.body = body
        if body_type == 'json':
            self.data = json.loads(self.body)
        elif body_type == 'yaml':
            self.data = yaml.load(self.body)
        self.uuid = self.data['uuid']

    @property
    def status(self):
        return self.resp.status

    @property
    def yaml_data(self):
        return yaml.load(self.body)

    @property
    def json_data(self):
        return json.loads(self.body)


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


def is_fedora():
    if os.path.exists("/etc/redhat-release"):
        return True
    return False
