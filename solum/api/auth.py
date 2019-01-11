#
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

import re

from keystonemiddleware import auth_token
from oslo_config import cfg
from oslo_log import log as logging
from pecan import hooks

from solum.common import context
from solum.i18n import _


LOG = logging.getLogger(__name__)

OPT_GROUP_NAME = 'keystone_authtoken'

AUTH_OPTS = [
    cfg.BoolOpt('enable_authentication',
                default=True,
                help='This option enables or disables user authentication '
                'via keystone. Default value is True.'),
]


def list_opts():
    yield None, AUTH_OPTS


CONF = cfg.CONF
CONF.register_opts(AUTH_OPTS)

PUBLIC_ENDPOINTS = [
    '^/?$',
    '^/v[0-9]+/?$',
    '^/v[0-9]+/triggers',
    '^/camp/platform_endpoints',
    '^/camp/camp_v1_1_endpoint'
]


def install(app, conf):
    if conf.get('enable_authentication'):
        return AuthProtocolWrapper(app, conf=dict(conf.get(OPT_GROUP_NAME)))
    else:
        LOG.warning(_('Keystone authentication is disabled by Solum '
                      'configuration parameter enable_authentication. '
                      'Solum will not authenticate incoming request. '
                      'In order to enable authentication set '
                      'enable_authentication option to True.'))

    return app


class AuthHelper(object):
    """Helper methods for Auth."""

    def __init__(self):
        endpoints_pattern = '|'.join(pe for pe in PUBLIC_ENDPOINTS)
        self._public_endpoints_regexp = re.compile(endpoints_pattern)

    def is_endpoint_public(self, path):
        return self._public_endpoints_regexp.match(path)


class AuthProtocolWrapper(auth_token.AuthProtocol):
    """A wrapper on Keystone auth_token AuthProtocol.

    Does not perform verification of authentication tokens for pub routes in
    the API. Public routes are those defined by PUBLIC_ENDPOINTS

    """

    def __call__(self, env, start_response):
        path = env.get('PATH_INFO')
        if AUTH.is_endpoint_public(path):
            return self._app(env, start_response)
        return super(AuthProtocolWrapper, self).__call__(env, start_response)


class ContextHook(hooks.PecanHook):

    def before(self, state):
        if not CONF.get('enable_authentication'):
            return
        # Skip authentication for public endpoints
        if AUTH.is_endpoint_public(state.request.path):
            return

        headers = state.request.headers
        user_id = headers.get('X-User-Id')
        roles = self._get_roles(state.request)
        project_id = headers.get('X-Project-Id')
        user_name = headers.get('X-User-Name', '')
        tenant_name = headers.get('X-Project')

        domain = headers.get('X-Domain-Name')
        project_domain_id = headers.get('X-Project-Domain-Id', '')
        user_domain_id = headers.get('X-User-Domain-Id', '')
        password = headers.get('X-Password', '')

        recv_auth_token = headers.get('X-Auth-Token',
                                      headers.get(
                                          'X-Storage-Token'))

        auth_token_info = state.request.environ.get('keystone.token_info')
        ctx = context.RequestContext(auth_token=recv_auth_token,
                                     auth_token_info=auth_token_info,
                                     user=user_id,
                                     tenant=project_id,
                                     domain=domain,
                                     user_domain=user_domain_id,
                                     project_domain=project_domain_id,
                                     user_name=user_name,
                                     roles=roles,
                                     password=password,
                                     tenant_name=tenant_name)
        state.request.security_context = ctx

    def _get_roles(self, req):
        """Get the list of roles."""

        if 'X-Roles' in req.headers:
            roles = req.headers.get('X-Roles', '')
        else:
            # Fallback to deprecated role header:
            roles = req.headers.get('X-Role', '')
            if roles:
                LOG.warning(_("X-Roles is missing. Using deprecated X-Role "
                              "header"))
        return [r.strip() for r in roles.split(',')]


AUTH = AuthHelper()
