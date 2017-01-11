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

import copy

from wsme import types as wtypes

from solum.api.controllers.camp.v1_1 import uris
from solum.api.controllers import common_types
from solum.api.controllers.v1.datamodel import types as api_types


class ParameterDefinitionLink(common_types.Link):
    """CAMP v1.1 ParameterLink attribute type."""

    required = bool
    """Indicates whether the parameter referenced by this Link is required."""

    default_value = wtypes.Base
    """Default value for the parameter referenced by this Link."""


class ParameterDefinitions(api_types.Base):
    """CAMP v1.1 parameter_definitions resource model."""

    parameter_definition_links = [ParameterDefinitionLink]
    """The value of the parameter_definition_links attribute is an array of
       extended Link elements that reference parameter_definition resources.
     """

    def __init__(self, **kwds):
        super(ParameterDefinitions, self).__init__(**kwds)

    def fix_uris(self, host_url):
        """Update URIs to reflect a host URL."""

        ret_val = copy.deepcopy(self)
        ret_val.uri = uris.PARAM_DEFS_URI_STR % (host_url, ret_val.uri)
        for pd_link in ret_val.parameter_definition_links:
            pd_link.href = uris.PARAM_DEF_URI_STR % (host_url, pd_link.href)

        return ret_val
