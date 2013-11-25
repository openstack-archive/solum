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
import wsme
from wsme import types as wtypes
import wsmeext.pecan as wsme_pecan

from solum.api.controllers import common_types


class Service(wtypes.Base):
    """The Service resource represents a networked service.

    You may create Component resources that refer to
    Service resources. The Component represents an instance of the Service.
    Your application connects to the Component that using a network protocol.
    For example, the Platform may offer a default Service named "mysql".
    You may create multiple Component resources that reference different
    instances of the "mysql" service. Each Component may be a multi-tenant
    instance of a MySQL database (perhaps a logical database) service offered
    by the Platform for a given Assembly.
    """

    uri = common_types.Uri
    "Uri to the Service"

    name = wtypes.text
    "Name of the Service"

    type = wtypes.text
    "Service type"

    description = wtypes.text
    "Description of the Service"

    tags = wtypes.text
    "Tags for the service"

    readOnly = bool
    "The service is read only"

    @classmethod
    def sample(cls):
        return cls(uri='http://example.com/v1/services/mysql',
                   name='mysql',
                   type='service',
                   description='A mysql service',
                   tags='group=xyz',
                   readOnly=False)


class ServiceController(rest.RestController):
    """Manages operations on a single service."""

    def __init__(self, service_id):
        pecan.request.context['service_id'] = service_id
        self._id = service_id

    @wsme_pecan.wsexpose(Service, wtypes.text)
    def get(self):
        """Return this service."""
        error = _("Not implemented")
        pecan.response.translatable_error = error
        raise wsme.exc.ClientSideError(unicode(error))

    @wsme_pecan.wsexpose(Service, wtypes.text, body=Service)
    def put(self, data):
        """Modify this service."""
        error = _("Not implemented")
        pecan.response.translatable_error = error
        raise wsme.exc.ClientSideError(unicode(error))

    @wsme_pecan.wsexpose(None, wtypes.text, status_code=204)
    def delete(self):
        """Delete this service."""
        error = _("Not implemented")
        pecan.response.translatable_error = error
        raise wsme.exc.ClientSideError(unicode(error))


class Services(wtypes.Base):
    """A summary of services returned on listing."""

    uri = common_types.Uri
    "Uri to the Services"

    type = wtypes.text
    "Services type"

    description = wtypes.text
    "Description of the Services"

    serviceLinks = [common_types.Link]
    "list of links to the available services"

    @classmethod
    def sample(cls):
        return cls(uri='http://example.com/v1/services',
                   type='services',
                   description='Collection of services',
                   serviceLinks=[common_types.Link(
                       href='http://example.com:9777/v1/services/y4',
                       targetName='y4')])


class ServicesController(rest.RestController):
    """Manages operations on the services collection."""

    @pecan.expose()
    def _lookup(self, service_id, *remainder):
        if remainder and not remainder[-1]:
            remainder = remainder[:-1]
        return ServiceController(service_id), remainder

    @wsme_pecan.wsexpose(Service, body=Service, status_code=201)
    def post(self, data):
        """Create a new service."""
        error = _("Not implemented")
        pecan.response.translatable_error = error
        raise wsme.exc.ClientSideError(unicode(error))

    @wsme_pecan.wsexpose(Services)
    def get_all(self):
        """Return the collection of services."""
        host_url = '/'.join([pecan.request.host_url, 'v1', 'services'])
        return Services(uri=host_url,
                        type='services',
                        description='The collection of available services',
                        serviceLinks=[])
