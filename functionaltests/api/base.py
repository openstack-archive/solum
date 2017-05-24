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
import random
import string
import time

from tempest.common import credentials_factory as common_creds
from tempest import config
from tempest.lib import auth
from tempest.lib.common import http
from tempest.lib.common import rest_client
import testtools
import yaml

from functionaltests.api.common import apputils


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

solum_group = config.cfg.OptGroup(name='solum', title='Solum test options')
SolumGroup = [
    config.cfg.BoolOpt('barbican_enabled',
                       default=False,
                       help="Defaults to false. Determines whether Barbican"
                            "is enabled."),
    config.cfg.BoolOpt('camp_enabled',
                       default=True,
                       help="Defaults to true. Determines whether CAMP"
                            "is enabled.")
]

CONF.register_group(solum_group)
CONF.register_opts(SolumGroup, group=solum_group.name)


class SolumClient(rest_client.RestClient):

    def __init__(self, auth_provider, service='application_deployment',
                 region='RegionOne'):
        super(SolumClient, self).__init__(auth_provider, service, region)
        self.endpoint_url = 'publicURL'
        self.created_assemblies = []
        self.created_plans = []
        self.created_apps = []
        self.created_lps = []

    def request_without_auth(self, resource, method, headers=None, body=None):
        if headers is None:
            headers = {}
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

    def create_lp(self, data=None):
        sample_lp = dict()
        s = string.lowercase
        sample_lp["name"] = "lp" + ''.join(random.sample(s, 5))
        lp_url = "https://github.com/murali44/Solum-lp-Go.git"
        sample_lp["source_uri"] = lp_url
        jsondata = json.dumps(sample_lp)
        resp, body = self.post('v1/language_packs', jsondata)
        return sample_lp["name"]

    def create_app(self, data=None):
        app_data = copy.deepcopy(data) or apputils.get_sample_data()
        json_data = json.dumps(app_data)
        resp, body = self.post('v1/apps', json_data)

        app_resp = SolumResponse(resp=resp, body=body, body_type='yaml')
        if app_resp.id is not None:
            self.created_apps.append(app_resp.id)
        return app_resp

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

    def delete_created_lps(self):
        resp, body = self.get('v1/language_packs')
        data = json.loads(body)
        [self._delete_language_pack(pl['uuid']) for pl in data]

    def _delete_language_pack(self, uuid):
        resp, _ = self.delete('v1/language_packs/%s' % uuid)

    def delete_language_pack(self, name):
        resp, _ = self.delete('v1/language_packs/%s' % name)

    def delete_created_apps(self):
        self.delete_created_assemblies()
        [self.delete_app(id) for id in list(self.created_apps)]
        self.created_apps = []

    def delete_app(self, id):
        resp, body = self.delete(
            'v1/apps/%s' % id,
            headers={'content-type': 'application/json'})
        if id in self.created_apps:
            self.created_apps.remove(id)
        return resp, body

    def delete_plan(self, uuid):
        resp, body = self.delete(
            'v1/plans/%s' % uuid,
            headers={'content-type': 'application/x-yaml'})
        self.created_plans.remove(uuid)
        return resp, body


class SolumResponse(object):
    def __init__(self, resp, body, body_type):
        self.resp = resp
        self.body = body
        if body_type == 'json':
            self.data = json.loads(self.body)
        elif body_type == 'yaml':
            self.data = yaml.safe_load(self.body)
        if self.data.get('uuid'):
            self.uuid = self.data.get('uuid')
        if self.data.get('id'):
            self.id = self.data.get('id')

    @property
    def status(self):
        return self.resp.status

    @property
    def yaml_data(self):
        return yaml.safe_load(self.body)

    @property
    def json_data(self):
        return json.loads(self.body)


class TestCase(testtools.TestCase):
    def setUp(self):
        super(TestCase, self).setUp()

        credentials = common_creds.get_configured_admin_credentials(
            'identity_admin')

        auth_provider = get_auth_provider(credentials)
        self.client = SolumClient(auth_provider)
        self.builderclient = SolumClient(auth_provider, 'image_builder')

    def tearDown(self):
        super(TestCase, self).tearDown()
        self.client.delete_created_apps()


def get_auth_provider(credentials, scope='project'):
    default_params = {
        'disable_ssl_certificate_validation':
            CONF.identity.disable_ssl_certificate_validation,
        'ca_certs': CONF.identity.ca_certificates_file,
        'trace_requests': CONF.debug.trace_requests
    }

    if isinstance(credentials, auth.KeystoneV3Credentials):
        auth_provider_class, auth_url = \
            auth.KeystoneV3AuthProvider, CONF.identity.uri_v3
    else:
        auth_provider_class, auth_url = \
            auth.KeystoneV2AuthProvider, CONF.identity.uri

    _auth_provider = auth_provider_class(credentials, auth_url,
                                         scope=scope,
                                         **default_params)
    _auth_provider.set_auth()
    return _auth_provider


def is_fedora():
    if os.path.exists("/etc/redhat-release"):
        return True
    return False


def config_set_as(config, target_value):
    value = getattr(CONF.solum, config)
    return value == target_value
