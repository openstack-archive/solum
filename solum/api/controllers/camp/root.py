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

from pecan import rest
from wsme import types as wtypes
import wsmeext.pecan as wsme_pecan

from solum.api.controllers.camp import camp_v1_1_endpoint
from solum.api.controllers.camp import platform_endpoints
from solum.api.controllers.camp.v1_1 import root as v1_1_root
from solum.common import exception


class Controller(rest.RestController):
    """CAMP API controller root."""

    platform_endpoints = platform_endpoints.PlatformEndpointsController()
    camp_v1_1_endpoint = camp_v1_1_endpoint.CAMPv11EndpointController()
    v1_1 = v1_1_root.Controller()

    @exception.wrap_wsme_controller_exception
    @wsme_pecan.wsexpose(wtypes.text)
    def get(self):
        return "CAMP be here"
