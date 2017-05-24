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


class Format(api_types.Base):
    """CAMP v1.1 format resource model."""

    mime_type = wtypes.text
    """This attribute contains the mime-type to be used by the Platform in
     HTTP [RFC2616] compliant content negotiation for this format."""

    version = wtypes.text
    """This attribute contains the version identifier of the data serialization
     format used."""

    documentation = common_types.Uri
    """ The value of this attribute is a URL reference to a document that
     describes this format."""

    def __init__(self, **kwds):
        super(Format, self).__init__(**kwds)

    def fix_uris(self, host_url):
        """Update URIs to reflect a host URL."""

        ret_val = copy.deepcopy(self)
        ret_val.uri = uris.FORMAT_URI_STR % (host_url, ret_val.uri)

        return ret_val
