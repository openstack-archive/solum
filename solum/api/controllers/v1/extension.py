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
import six
import wsme
from wsme import types as wtypes
import wsmeext.pecan as wsme_pecan

from solum.api.controllers.v1.datamodel import extension
from solum.api.handlers import extension_handler
from solum.common import exception


class ExtensionController(rest.RestController):
    """Manages operations on a single extension."""

    def __init__(self, extension_id):
        pecan.request.context['extension_id'] = extension_id
        self._id = extension_id

    @wsme_pecan.wsexpose(extension.Extension, wtypes.text)
    def get(self):
        """Return this extension."""
        try:
            handler = extension_handler.ExtensionHandler()
            return handler.get(self._id)
        except exception.SolumException as excp:
            pecan.response.translatable_error = excp
            raise wsme.exc.ClientSideError(six.text_type(excp), excp.code)


class ExtensionsController(rest.RestController):
    """Manages operations on the extensions collection."""

    @pecan.expose()
    def _lookup(self, extension_id, *remainder):
        if remainder and not remainder[-1]:
            remainder = remainder[:-1]
        return ExtensionController(extension_id), remainder

    @wsme_pecan.wsexpose([extension.Extension])
    def get_all(self):
        """Return all extensions, based on the query provided."""
        return []
