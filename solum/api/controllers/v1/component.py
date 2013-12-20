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

from solum.api.controllers.v1.datamodel import component
from solum.api.handlers import component_handler as componenthandler
from solum.common import exception as solum_exception


class ComponentController(rest.RestController):
    """Manages operations on a single component."""

    def __init__(self, component_id):
        pecan.request.context['component_id'] = component_id
        self._id = component_id

    @wsme_pecan.wsexpose(component.Component, wtypes.text)
    def get(self):
        """Return this component."""
        try:
            handler = componenthandler.ComponentHandler()
            return handler.get(self._id)
        except solum_exception.SolumException as excp:
            pecan.response.translatable_error = excp
            raise wsme.exc.ClientSideError(six.text_type(excp), excp.code)

    @wsme_pecan.wsexpose(component.Component, wtypes.text,
                         body=component.Component)
    def put(self, data):
        """Modify this component."""
        try:
            handler = componenthandler.ComponentHandler()
            return handler.update(data)
        except solum_exception.SolumException as excp:
            pecan.response.translatable_error = excp
            raise wsme.exc.ClientSideError(six.text_type(excp), excp.code)

    @wsme_pecan.wsexpose(None, wtypes.text, status_code=204)
    def delete(self):
        """Delete this component."""
        try:
            handler = componenthandler.ComponentHandler()
            return handler.delete(self._id)
        except solum_exception.SolumException as excp:
            pecan.response.translatable_error = excp
            raise wsme.exc.ClientSideError(six.text_type(excp), excp.code)


class ComponentsController(rest.RestController):
    """Manages operations on the components collection."""

    @pecan.expose()
    def _lookup(self, component_id, *remainder):
        if remainder and not remainder[-1]:
            remainder = remainder[:-1]
        return ComponentController(component_id), remainder

    @wsme_pecan.wsexpose(component.Component, body=component.Component,
                         status_code=201)
    def post(self, data):
        """Create a new component."""
        try:
            handler = componenthandler.ComponentHandler()
            return handler.create(data)
        except solum_exception.SolumException as excp:
            pecan.response.translatable_error = excp
            raise wsme.exc.ClientSideError(six.text_type(excp), excp.code)

    @wsme_pecan.wsexpose([component.Component])
    def get_all(self):
        """Return all components, based on the query provided."""
        try:
            handler = componenthandler.ComponentHandler()
            return handler.get_all()
        except solum_exception.SolumException as excp:
            pecan.response.translatable_error = excp
            raise wsme.exc.ClientSideError(six.text_type(excp), excp.code)
