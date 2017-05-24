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


class Platform(api_types.Base):
    """CAMP v1.1 platform resource."""

    supported_formats_uri = common_types.Uri
    """This attribute is a URL reference to the formats resource for the
     purpose of identifying all supported formats for this platform."""

    extensions_uri = common_types.Uri
    """This attribute is a URL reference to the extensions resource that
     identifies the extensions supported by this platform."""

    type_definitions_uri = common_types.Uri
    """This attribute is a URL reference to the type_definitions resource that
     provides information on the resource types that the Platform supports."""

    platform_endpoints_uri = common_types.Uri
    """This attribute is a URL reference to the platform_endpoints resource."""

    specification_version = wtypes.text
    """The value of this attribute is the Specification Version String of the
     CAMP specification that is supported by the resources rooted in this
     platform."""

    implementation_version = wtypes.text
    """The value of this attribute is a string that expresses the
     provider-specific implementation version supported by the resources
     rooted in this platform."""

    assemblies_uri = common_types.Uri
    """This attribute is a URL reference to the assemblies resource."""

    services_uri = common_types.Uri
    """This attribute is a URL reference to the services resource."""

    plans_uri = common_types.Uri
    """This attribute is a URL reference to the plans resource."""

    def __init__(self, **kwds):
        super(Platform, self).__init__(**kwds)
