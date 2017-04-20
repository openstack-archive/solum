# Copyright 2014 - Red Hat Inc.
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

from barbicanclient import client as barbicanclient
from keystoneauth1 import loading

from oslo_config import cfg


class BarbicanClient(object):
    """Barbican client wrapper so we can encapsulate logic in one place."""

    def __init__(self, verify=True):
        self._admin_client = None

    @property
    def admin_client(self):
        if not self._admin_client:
            # Create connection to API
            self._admin_client = self._barbican_admin_init()
        return self._admin_client

    def _barbican_admin_init(self):
        # Import auth_token to have keystone_authtoken settings setup.
        auth = loading.load_auth_from_conf_options(
            cfg.CONF, 'keystone_authtoken')
        sess = loading.load_session_from_conf_options(
            cfg.CONF, 'keystone_authtoken', auth=auth)
        return barbicanclient.Client(session=sess)
