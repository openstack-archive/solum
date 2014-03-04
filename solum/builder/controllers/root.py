# Copyright 2014 - Rackspace Hosting
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

import pecan
import wsmeext.pecan as wsme_pecan

from solum.api.controllers import common_types
from solum.api.controllers import root as api_root
from solum.builder.controllers.v1 import root as v1_root


class RootController(object):

    v1 = v1_root.Controller()

    @wsme_pecan.wsexpose([api_root.Version])
    def index(self):
        host_url = '%s/%s' % (pecan.request.host_url, 'v1')
        v1 = api_root.Version(id='v1.0',
                              status='CURRENT',
                              link=common_types.Link(target_name='v1',
                                                     href=host_url))
        return [v1]
