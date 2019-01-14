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

from oslo_config import cfg
import pecan
from wsme import types as wtypes
import wsmeext.pecan as wsme_pecan

from solum.api.controllers.camp import root as camp_root
from solum.api.controllers import common_types
from solum.api.controllers.v1 import root as v1_root


STATUS_KIND = wtypes.Enum(str, 'SUPPORTED', 'CURRENT', 'DEPRECATED')

camp_group = cfg.OptGroup(name='camp',
                          title='Options that apply to the CAMP API')

CAMP_API_OPTS = [
    cfg.BoolOpt('camp_enabled',
                default=True,
                help=("Enable/disable support for the OASIS CAMP "
                      "API. Default value is True."))
]


def list_opts():
    yield camp_group, CAMP_API_OPTS


CONF = cfg.CONF
CONF.register_group(camp_group)
CONF.register_opts(CAMP_API_OPTS, group=camp_group)


class Version(wtypes.Base):
    """Version representation."""

    id = wtypes.text
    "The version identifier."

    status = STATUS_KIND
    "The status of the API (SUPPORTED, CURRENT or DEPRECATED)."

    link = common_types.Link
    "The link to the versioned API."

    @classmethod
    def sample(cls):
        return cls(id='v1.0',
                   status='CURRENT',
                   link=common_types.Link(target_name='v1',
                                          href='http://example.com:9777/v1'))


class RootController(object):

    v1 = v1_root.Controller()

    if CONF.camp.camp_enabled:
        camp = camp_root.Controller()

    @wsme_pecan.wsexpose([Version])
    def index(self):
        base_url = pecan.request.application_url.rstrip('/')
        host_url = '%s/%s' % (base_url, 'v1')
        v1 = Version(id='v1.0',
                     status='CURRENT',
                     link=common_types.Link(target_name='v1',
                                            href=host_url))
        return [v1]
