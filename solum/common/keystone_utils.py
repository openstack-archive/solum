# Copyright 2015 - Rackspace Hosting.
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

"""Utilities and helper functions for keystone integration."""

from oslo_config import cfg

from solum.common import clients
from solum.common import context


def create_delegation_context(assembly_obj, ctx=None):
    """Create a delegated security context."""
    if cfg.CONF.get('keystone_version') == '3':
        cntx = context.RequestContext(trust_id=assembly_obj.trust_id)
        kc = clients.OpenStackClients(cntx).keystone()
        return kc.context


def delete_delegation_token(user_ctx, trust_id):
    if cfg.CONF.get('keystone_version') == '3':
        ksc = clients.OpenStackClients(user_ctx).keystone()
        ksc.delete_trust(trust_id)


def create_delegation_token(user_ctx):
    if cfg.CONF.get('keystone_version') == '3':
        ksc = clients.OpenStackClients(user_ctx).keystone()
        trust_context = ksc.create_trust_context()
        return trust_context.trust_id
