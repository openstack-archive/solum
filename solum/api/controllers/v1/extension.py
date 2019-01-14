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
from wsme import types as wtypes
import wsmeext.pecan as wsme_pecan

from solum.api.controllers.v1.datamodel import extension
from solum.api.handlers import extension_handler
from solum.common import exception
from solum.common import policy
from solum import objects


class ExtensionController(rest.RestController):
    """Manages operations on a single extension."""

    def __init__(self, extension_id):
        self._id = extension_id

    @exception.wrap_wsme_pecan_controller_exception
    @wsme_pecan.wsexpose(extension.Extension, wtypes.text)
    def get(self):
        """Return this extension."""
        policy.check('show_extension',
                     pecan.request.security_context)
        handler = extension_handler.ExtensionHandler(
            pecan.request.security_context)
        host_url = pecan.request.application_url.rstrip('/')
        return extension.Extension.from_db_model(handler.get(self._id),
                                                 host_url)

    @exception.wrap_wsme_pecan_controller_exception
    @wsme_pecan.wsexpose(extension.Extension, wtypes.text,
                         body=extension.Extension)
    def put(self, data):
        """Modify this extension."""
        policy.check('update_extension',
                     pecan.request.security_context)
        handler = extension_handler.ExtensionHandler(
            pecan.request.security_context)
        obj = handler.update(self._id,
                             data.as_dict(objects.registry.Extension))
        host_url = pecan.request.application_url.rstrip('/')
        return extension.Extension.from_db_model(obj, host_url)

    @exception.wrap_wsme_pecan_controller_exception
    @wsme_pecan.wsexpose(None, wtypes.text, status_code=204)
    def delete(self):
        """Delete this extension."""
        policy.check('delete_extension',
                     pecan.request.security_context)
        handler = extension_handler.ExtensionHandler(
            pecan.request.security_context)
        handler.delete(self._id)


class ExtensionsController(rest.RestController):
    """Manages operations on the extensions collection."""

    @pecan.expose()
    def _lookup(self, extension_id, *remainder):
        if remainder and not remainder[-1]:
            remainder = remainder[:-1]
        return ExtensionController(extension_id), remainder

    @exception.wrap_wsme_pecan_controller_exception
    @wsme_pecan.wsexpose(extension.Extension, wtypes.text,
                         body=extension.Extension,
                         status_code=201)
    def post(self, data):
        """Create a new extension."""
        policy.check('create_extension',
                     pecan.request.security_context)
        handler = extension_handler.ExtensionHandler(
            pecan.request.security_context)
        obj = handler.create(data.as_dict(objects.registry.Extension))
        host_url = pecan.request.application_url.rstrip('/')
        return extension.Extension.from_db_model(obj, host_url)

    @exception.wrap_wsme_pecan_controller_exception
    @wsme_pecan.wsexpose([extension.Extension])
    def get_all(self):
        """Return all extensions, based on the query provided."""
        policy.check('get_extensions',
                     pecan.request.security_context)
        handler = extension_handler.ExtensionHandler(
            pecan.request.security_context)
        host_url = pecan.request.application_url.rstrip('/')
        return [extension.Extension.from_db_model(obj, host_url)
                for obj in handler.get_all()]
