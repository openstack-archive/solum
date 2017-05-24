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

from solum.api.controllers import common_types
from solum.api.controllers.v1.datamodel import types as api_types


class PlatformEndpoints(api_types.Base):
    """platform_endpoints resource model."""

    platform_endpoint_links = [common_types.Link]
    """ Links to the platform_endpoint resources for this deployment. """

    def __init__(self, **kwds):
        super(PlatformEndpoints, self).__init__(**kwds)
