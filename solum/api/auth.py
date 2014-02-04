# -*- encoding: utf-8 -*-
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

from keystoneclient.middleware import auth_token
from oslo.config import cfg

from solum.openstack.common.gettextutils import _
from solum.openstack.common import log as logging


LOG = logging.getLogger(__name__)

OPT_GROUP_NAME = 'keystone_authtoken'

auth_opts = [
    cfg.StrOpt('enable_authentication',
               default='True',
               help='This option enables or disables user authentication '
               'via keystone. Default value is True.'),
]

CONF = cfg.CONF
CONF.register_opts(auth_opts)
CONF.register_opts(auth_token.opts, group=OPT_GROUP_NAME)


def install(app, conf):
    if conf.get('enable_authentication').lower() == 'true':
        return AuthProtocolWrapper(app, conf=dict(conf.get(OPT_GROUP_NAME)))
    else:
        LOG.warning(_('Keystone authentication is disabled by Solum '
                      'configuration parameter enable_authentication. '
                      'Solum will not authenticate incoming request. '
                      'In order to enable authentication set '
                      'enable_authentication option to True.'))

    return app


class AuthProtocolWrapper(auth_token.AuthProtocol):
    """A wrapper on Keystone auth_token AuthProtocol.

    Does not perform verification of authentication tokens for pub routes in
    the API. Public routes are those which Uri starts with
    '/{version_number}/pub/'

    """

    def __call__(self, env, start_response):
        path = env.get('PATH_INFO')
        regexp = re.compile('^/v[0-9]+/public/')
        if regexp.match(path):
            return self.app(env, start_response)
        return super(AuthProtocolWrapper, self).__call__(env, start_response)
