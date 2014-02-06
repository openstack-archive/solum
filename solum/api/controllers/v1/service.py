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

from solum.api.controllers.v1.datamodel import service
from solum.api.handlers import service_handler
from solum.common import exception
from solum.openstack.common.gettextutils import _


class ServiceController(rest.RestController):
    """Manages operations on a single service."""

    def __init__(self, service_id):
        pecan.request.context['service_id'] = service_id
        self._id = service_id

    @exception.wrap_controller_exception
    @wsme_pecan.wsexpose(service.Service, wtypes.text)
    def get(self):
        """Return this service."""
        handler = service_handler.ServiceHandler()
        return handler.get(self._id)

    @wsme_pecan.wsexpose(service.Service, wtypes.text, body=service.Service)
    def put(self, data):
        """Modify this service."""
        error = _("Not implemented")
        pecan.response.translatable_error = error
        raise wsme.exc.ClientSideError(six.text_type(error))

    @wsme_pecan.wsexpose(None, wtypes.text, status_code=204)
    def delete(self):
        """Delete this service."""
        error = _("Not implemented")
        pecan.response.translatable_error = error
        raise wsme.exc.ClientSideError(six.text_type(error))


class ServicesController(rest.RestController):
    """Manages operations on the services collection."""

    @pecan.expose()
    def _lookup(self, service_id, *remainder):
        if remainder and not remainder[-1]:
            remainder = remainder[:-1]
        return ServiceController(service_id), remainder

    @wsme_pecan.wsexpose(service.Service, body=service.Service,
                         status_code=201)
    def post(self, data):
        """Create a new service."""
        error = _("Not implemented")
        pecan.response.translatable_error = error
        raise wsme.exc.ClientSideError(six.text_type(error))

    @wsme_pecan.wsexpose([service.Service])
    def get_all(self):
        """Return the collection of services."""
        return []
