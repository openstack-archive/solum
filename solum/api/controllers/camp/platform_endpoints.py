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

from solum.api.controllers.camp import camp_v1_1_endpoint as endpoint
from solum.api.controllers.camp.datamodel import platform_endpoints as model
from solum.api.controllers import common_types
from solum.common import exception


URI_STRING = '%s/camp/platform_endpoints'
DESCRIPTION_STRING = "Solum CAMP API platform_endpoints resource."


class PlatformEndpointsController(rest.RestController):
    """platform_endpoints resource controller."""

    @exception.wrap_wsme_controller_exception
    @wsme_pecan.wsexpose(model.PlatformEndpoints)
    def get(self):
        host_url = pecan.request.application_url.rstrip('/')
        links = [
            common_types.Link(href=endpoint.URI_STRING % host_url,
                              target_name=endpoint.NAME_STRING)
        ]

        return model.PlatformEndpoints(uri=URI_STRING % host_url,
                                       name='Solum_CAMP_endpoints',
                                       type='platform_endpoints',
                                       description=DESCRIPTION_STRING,
                                       platform_endpoint_links=links)
