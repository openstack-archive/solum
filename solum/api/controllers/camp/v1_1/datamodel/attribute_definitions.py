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

from pecan import core
from wsme import types as wtypes

from solum.api.controllers.camp.v1_1 import uris
from solum.api.controllers.v1.datamodel import types as api_types


class AttributeDefinition(api_types.Base):
    """attribute_definition resource

    An attribute_definition resource represents exactly one supported
    attribute of one or more resource types.
    """

    documentation = wtypes.text
    """The value of the documentation attribute is a URI that references the
     documentation for the attribute that this resource describes."""

    attribute_type = wtypes.text
    """The value of the attribute_type attribute specifies the type of the
     attribute that this resource describes."""

    @classmethod
    def from_json(cls, dct):
        ret_val = cls()
        for key, value in dct.items():
            if hasattr(ret_val, key):
                setattr(ret_val, key, value)
            else:
                core.abort(500, 'internal metadata is incorrect')
        return ret_val

    def fix_uris(self, host_url):
        """Update URIs to reflect a host URL."""
        ret_val = copy.deepcopy(self)
        ret_val.uri = uris.ATTRIBUTE_DEF_URI_STR % (host_url, ret_val.uri)
        return ret_val
