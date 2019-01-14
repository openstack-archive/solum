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
from pecan import core
from pecan import rest
from wsme import types as wtypes
import wsmeext.pecan as wsme_pecan

from solum.api.controllers.camp.v1_1.datamodel import format
from solum.api.controllers.camp.v1_1.datamodel import formats
from solum.api.controllers.camp.v1_1 import uris
from solum.api.controllers import common_types
from solum.api.handlers.camp import format_handler
from solum.common import exception


DESCRIPTION_STRING = "Solum CAMP API supported formats collection resource."


class FormatsController(rest.RestController):
    """Manages operations on CAMP's formats resource."""

    @exception.wrap_wsme_controller_exception
    @wsme_pecan.wsexpose(format.Format, wtypes.text)
    def get_one(self, format_name):
        """Return the appropriate format resource."""
        handler = (format_handler.
                   FormatHandler(pecan.request.security_context))
        raw_format = handler.get(format_name)
        if not raw_format:
            core.abort(404,
                       '%s is not a format resource' %
                       format_name)
        host_url = pecan.request.application_url.rstrip('/')
        return raw_format.fix_uris(host_url)

    @exception.wrap_wsme_controller_exception
    @wsme_pecan.wsexpose(formats.Formats)
    def get(self):
        """Return the formats resource."""
        host_url = pecan.request.application_url.rstrip('/')
        links = [common_types.Link(href=uris.JSON_FORMAT_URI_STR % host_url,
                                   target_name=uris.JSON_FORMAT_NAME_STR)]
        return formats.Formats(uri=uris.FORMATS_URI_STR % host_url,
                               name='Solum_CAMP_formats',
                               type='formats',
                               description=DESCRIPTION_STRING,
                               format_links=links)
