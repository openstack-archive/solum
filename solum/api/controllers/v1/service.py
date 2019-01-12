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
import wsmeext.pecan as wsme_pecan

from solum.api.controllers.v1.datamodel import service
from solum.api.handlers import service_handler
from solum.common import exception
from solum.common import policy
from solum import objects


class ServiceController(rest.RestController):
    """Manages operations on a single service."""

    def __init__(self, service_id):
        super(ServiceController, self).__init__()
        self._id = service_id

    @exception.wrap_wsme_pecan_controller_exception
    @wsme_pecan.wsexpose(service.Service)
    def get(self):
        """Return this service."""
        policy.check('show_service',
                     pecan.request.security_context)
        handler = service_handler.ServiceHandler(
            pecan.request.security_context)
        host_url = pecan.request.application_url.rstrip('/')
        return service.Service.from_db_model(handler.get(self._id), host_url)

    @exception.wrap_wsme_pecan_controller_exception
    @wsme_pecan.wsexpose(service.Service, body=service.Service)
    def put(self, data):
        """Modify this service."""
        policy.check('update_service',
                     pecan.request.security_context)
        handler = service_handler.ServiceHandler(
            pecan.request.security_context)
        res = handler.update(self._id,
                             data.as_dict(objects.registry.Service))
        host_url = pecan.request.application_url.rstrip('/')
        return service.Service.from_db_model(res, host_url)

    @exception.wrap_wsme_pecan_controller_exception
    @wsme_pecan.wsexpose(status_code=204)
    def delete(self):
        """Delete this service."""
        policy.check('delete_service',
                     pecan.request.security_context)
        handler = service_handler.ServiceHandler(
            pecan.request.security_context)
        return handler.delete(self._id)


class ServicesController(rest.RestController):
    """Manages operations on the services collection."""

    @pecan.expose()
    def _lookup(self, service_id, *remainder):
        if remainder and not remainder[-1]:
            remainder = remainder[:-1]
        return ServiceController(service_id), remainder

    @exception.wrap_wsme_pecan_controller_exception
    @wsme_pecan.wsexpose(service.Service, body=service.Service,
                         status_code=201)
    def post(self, data):
        """Create a new service."""
        policy.check('create_service',
                     pecan.request.security_context)
        handler = service_handler.ServiceHandler(
            pecan.request.security_context)
        host_url = pecan.request.application_url.rstrip('/')
        return service.Service.from_db_model(
            handler.create(data.as_dict(objects.registry.Service)), host_url)

    @exception.wrap_wsme_pecan_controller_exception
    @wsme_pecan.wsexpose([service.Service])
    def get_all(self):
        """Return all services, based on the query provided."""
        policy.check('get_services',
                     pecan.request.security_context)
        handler = service_handler.ServiceHandler(
            pecan.request.security_context)
        host_url = pecan.request.application_url.rstrip('/')
        return [service.Service.from_db_model(ser, host_url)
                for ser in handler.get_all()]
