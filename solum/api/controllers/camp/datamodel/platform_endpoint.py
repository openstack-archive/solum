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

from wsme import types as wtypes

from solum.api.controllers import common_types
from solum.api.controllers.v1.datamodel import types as api_types


class PlatformEndpoint(api_types.Base):
    """CAMP v1.1 platform_endpoint resource model."""

    platform_uri = common_types.Uri
    """The URI of the platform resource that this platform_endpoint resource
       describes."""

    specification_version = wtypes.text
    """Specification Version String of the CAMP spec supported by the platform
       referenced by this resource."""

    backward_compatible_specification_versions = [wtypes.text]
    """Identifies each version of the CAMP spec that is backwards compatible
       with the spec supported by the platform referenced by this resource."""

    implementation_version = wtypes.text
    """Provider specific implementation version supported by the platform
       referenced by this resource."""

    backward_compatible_implementation_versions = [wtypes.text]
    """Identifies each implementation version that is backwards compatible with
       the implementation version of the platform referenced by this
       resource."""

    auth_scheme = wtypes.text
    """Indicates the authentication scheme/mechanism expected by the referenced
       platform resource."""

    def __init__(self, **kwds):
        super(PlatformEndpoint, self).__init__(**kwds)
