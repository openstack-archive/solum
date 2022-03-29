# Copyright 2014 - Rackspace Hosting.
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

from keystoneauth1 import identity
from keystoneauth1 import loading as ka_loading
from keystoneauth1 import session as ks_session
import keystoneclient.exceptions as kc_exception
from keystoneclient.v3 import client as kc_v3
from oslo_config import cfg
from oslo_log import log as logging
from oslo_utils import importutils

from solum.common import context
from solum.common import exception
from solum.i18n import _

LOG = logging.getLogger(__name__)

trust_opts = [
    cfg.ListOpt('trusts_delegated_roles',
                default=['solum_assembly_update'],
                help=_('Subset of trustor roles to be delegated to solum.')),
]
cfg.CONF.register_opts(trust_opts)
cfg.CONF.import_opt('www_authenticate_uri', 'keystonemiddleware.auth_token',
                    group='keystone_authtoken')

AUTH_OPTS = [
    cfg.StrOpt('keystone_version',
               default='3',
               help='The keystone version to use with Solum'),
]


def list_opts():
    yield None, AUTH_OPTS
    yield None, trust_opts


cfg.CONF.register_opts(AUTH_OPTS)

cfg.CONF.import_opt('lp_operator_user', 'solum.worker.config', group='worker')
cfg.CONF.import_opt('lp_operator_password',
                    'solum.worker.config', group='worker')
cfg.CONF.import_opt('lp_operator_tenant_name',
                    'solum.worker.config', group='worker')


class KeystoneClient(object):
    """Keystone client wrapper to initialize the right version of the client.

       The version to use is specified in solum.conf
       """

    def __new__(self, context):
        ks_version = cfg.CONF.get('keystone_version')
        if ks_version == '3':
            return KeystoneClientV3(context)
        else:
            msg = 'Unsupported version of keystone: %s', ks_version
            LOG.error(msg)
            raise exception.AuthorizationFailure(client='keystone',
                                                 message=msg)


class KeystoneClientV3(object):
    """Keystone client wrapper so we can encapsulate logic in one place."""

    def __init__(self, context):
        # If a trust_id is specified in the context, we immediately
        # authenticate so we can populate the context with a trust token
        # otherwise, we delay client authentication until needed to avoid
        # unnecessary calls to keystone.
        #
        # Note that when you obtain a token using a trust, it cannot be
        # used to reauthenticate and get another token, so we have to
        # get a new trust-token even if context.auth_token is set.
        #
        # - context.auth_url is expected to contain a versioned keystone
        #   path, we will work with either a v2.0 or v3 path
        self.context = context
        self._client = None
        self._admin_client = None
        self._lp_admin_client = None

        if self.context and self.context.auth_url:
            self.endpoint = self.context.auth_url.replace('v2.0', 'v3')
        else:
            # Import auth_token to have keystone_authtoken settings setup.
            importutils.import_module('keystonemiddleware.auth_token')
            self.endpoint = \
                cfg.CONF.keystone_authtoken.www_authenticate_uri.replace(
                    'v2.0', 'v3')

        if self.context and self.context.trust_id:
            # Create a client with the specified trust_id, this
            # populates self.context.auth_token with a trust-scoped token
            self._client = self._v3_client_init()

    @property
    def client(self):
        if not self._client:
            # Create connection to v3 API
            self._client = self._v3_client_init()
        return self._client

    @property
    def admin_client(self):
        if not self._admin_client:
            # Create admin client connection to v3 API
            admin_creds = self._service_admin_creds()
            auth = identity.Password(**admin_creds)
            session = ks_session.Session(auth=auth)
            c = kc_v3.Client(session=session)
            self._admin_client = c
        return self._admin_client

    @property
    def lp_admin_client(self):
        if not self._lp_admin_client:
            # Create lp operator client connection to v3 API
            lp_operator_creds = self._lp_operator_creds()
            auth = identity.Password(**lp_operator_creds)
            session = ks_session.Session(auth=auth)
            c = kc_v3.Client(session=session)
            self._lp_admin_client = c
        return self._lp_admin_client

    def _v3_client_init(self):
        kwargs = {
            'auth_url': self.endpoint,
            'endpoint': self.endpoint
        }
        # Note try trust_id first, as we can't reuse auth_token in that case
        if self.context.trust_id is not None:
            # We got a trust_id, so we use the admin credentials
            # to authenticate with the trust_id so we can use the
            # trust impersonating the trustor user.
            kwargs.update(self._service_admin_creds())
            kwargs['trust_id'] = self.context.trust_id
            kwargs.pop('project_name')
            auth = ka_loading.load_auth_from_conf_options(
                cfg.CONF, 'keystone_authtoken', **kwargs)
        elif self.context.auth_token is not None:
            kwargs['token'] = self.context.auth_token
            kwargs['project_id'] = self.context.project_id
            auth = identity.Token(
                auth_url=kwargs['auth_url'],
                token=kwargs['token'],
                project_id=kwargs['project_id'])
        else:
            LOG.error(_("Keystone v3 API connection failed, no password "
                        "trust or auth_token!"))
            raise exception.AuthorizationFailure()
        session = ks_session.Session(auth=auth)
        client = kc_v3.Client(session=session)
        client.auth_ref = client.session.auth.get_access(client.session)
        # If we are authenticating with a trust set the context auth_token
        # with the trust scoped token
        if 'trust_id' in kwargs:
            # Sanity check
            if not client.auth_ref.trust_scoped:
                LOG.error(_("trust token re-scoping failed!"))
                raise exception.AuthorizationFailure()
            # All OK so update the context with the token
            self.context.auth_token = client.auth_ref.auth_token
            self.context.auth_url = self.endpoint
            self.context.user = client.auth_ref.user_id
            self.context.project_id = client.auth_ref.project_id
            self.context.user_name = client.auth_ref.username

        return client

    def _service_admin_creds(self):
        # Import auth_token to have keystone_authtoken settings setup.
        importutils.import_module('keystonemiddleware.auth_token')
        creds = {
            'username': cfg.CONF.keystone_authtoken.username,
            'password': cfg.CONF.keystone_authtoken.password,
            'auth_url': self.endpoint,
            'project_name': cfg.CONF.keystone_authtoken.project_name,
            'user_domain_name': "Default",
            'project_domain_name': "Default"}
        return creds

    def _lp_operator_creds(self):
        # Get LP Operator creds from config.
        creds = {
            'username': cfg.CONF.worker.lp_operator_user,
            'password': cfg.CONF.worker.lp_operator_password,
            'auth_url': self.endpoint,
            'project_name': cfg.CONF.worker.lp_operator_tenant_name,
            'user_domain_name': "Default",
            'project_domain_name': "Default"}
        return creds

    def create_trust_context(self):
        """Create a trust using the trustor identity in the current context.

        Use the trustee as the solum service user and return a context
        containing the new trust_id.

        If the current context already contains a trust_id, we do nothing
        and return the current context.
        """
        if self.context.trust_id:
            return self.context

        trustee_user_id = self.admin_client.session.auth.get_user_id(
            self.admin_client.session)
        auth_ref = self.client.session.auth.get_access(self.client.session)
        trustor_user_id = auth_ref.user_id
        trustor_project_id = auth_ref.project_id
        roles = cfg.CONF.trusts_delegated_roles
        trust = self.client.trusts.create(trustor_user=trustor_user_id,
                                          trustee_user=trustee_user_id,
                                          project=trustor_project_id,
                                          impersonation=True,
                                          role_names=roles)

        trust_context = context.RequestContext.from_dict(
            self.context.to_dict())
        trust_context.trust_id = trust.id
        return trust_context

    def delete_trust(self, trust_id):
        """Delete the specified trust."""
        try:
            self.client.trusts.delete(trust_id)
        except kc_exception.NotFound:
            pass

    @property
    def auth_token(self):
        auth_ref = self.client.session.auth.get_access(self.client.session)
        return auth_ref.auth_token
