# Copyright 2014 - Mirantis, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import inspect

from oslo_config import cfg
from oslo_context import context

AUTH_OPTS = [
    cfg.StrOpt('solum_admin_tenant_id',
               default='',
               help='Tenant id of global admin'),
]


def list_opts():
    yield None, AUTH_OPTS


CONF = cfg.CONF
CONF.register_opts(AUTH_OPTS)


class RequestContext(context.RequestContext):
    def __init__(self, auth_token=None, user=None, tenant=None, domain=None,
                 user_domain=None, project_domain=None, is_admin=False,
                 read_only=False, request_id=None, user_name=None, roles=None,
                 auth_url=None, trust_id=None, auth_token_info=None,
                 password=None, tenant_name=None):
        super(RequestContext, self).__init__(auth_token=auth_token,
                                             user=user,
                                             tenant=tenant,
                                             domain=domain,
                                             user_domain=user_domain,
                                             project_domain=project_domain,
                                             is_admin=is_admin,
                                             read_only=read_only,
                                             show_deleted=False,
                                             request_id=request_id,
                                             roles=roles)
        self.user_name = user_name
        self.auth_url = auth_url
        self.trust_id = trust_id
        self.auth_token_info = auth_token_info
        self.password = password
        self.tenant_name = tenant_name
        global_admin_id = CONF.get('solum_admin_tenant_id')
        if global_admin_id and global_admin_id == tenant:
            self.is_admin = True

    def to_dict(self):
        values = super(RequestContext, self).to_dict()
        values.update({
            'user_name': self.user_name,
            'auth_url': self.auth_url,
            'auth_token_info': self.auth_token_info,
            'trust_id': self.trust_id})
        return values

    @classmethod
    def from_dict(cls, values):
        allowed = [arg for arg in
                   inspect.getargspec(RequestContext.__init__).args
                   if arg != 'self']
        kwargs = dict((k, v) for (k, v) in values.items() if k in allowed)
        return cls(**kwargs)
