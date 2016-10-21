# Copyright 2014 - Rackspace Hosting
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

from oslo_config import cfg
from pecan import hooks

OPTS = [
    cfg.StrOpt('release',
               default='openstack',
               help='The current build of Solum.'),
]


def list_opts():
    yield None, OPTS


CONF = cfg.CONF
CONF.register_opts(OPTS)


class ReleaseReporter(hooks.PecanHook):
    priority = 99

    def after(self, state):
        release_info = CONF.get('release')
        if release_info is not None:
            release_dict = {
                'X-Solum-Release': release_info,
            }
            state.response.headers.update(release_dict)
