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
from pecan import rest
import wsmeext.pecan as wsme_pecan

from solum.api.controllers.camp.datamodel import platform_endpoint as model
from solum.api.controllers.camp.v1_1 import uris
from solum.common import exception


URI_STRING = '%s/camp/camp_v1_1_endpoint'
NAME_STRING = 'Solum_CAMP_v1_1_endpoint'
DESCRIPTION_STRING = "Solum CAMP v1.1 API platform_endpoint resource."


class CAMPv11EndpointController(rest.RestController):
    """camp_v1_1_endpoint resource controller."""

    @exception.wrap_wsme_controller_exception
    @wsme_pecan.wsexpose(model.PlatformEndpoint)
    def get(self):
        host_url = pecan.request.application_url.rstrip('/')
        return model.PlatformEndpoint(uri=URI_STRING % host_url,
                                      name=NAME_STRING,
                                      type='platform_endpoint',
                                      description=DESCRIPTION_STRING,
                                      platform_uri=uris.PLATFORM_URI_STR %
                                      host_url,
                                      specification_version='CAMP 1.1',
                                      implementation_version='Solum CAMP 1.1',
                                      auth_scheme='KEYSTONE-2.0')
