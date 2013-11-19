# Copyright 2013 - Red Hat, Inc.
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
from pecan import rest
import wsme
from wsme import types as wtypes
import wsmeext.pecan as wsme_pecan

from solum.api.controllers import common_types
from solum import version


class Assembly(wtypes.Base):
    """Representation of an Assembly.

    The Assembly resource represents a group of components that make
    up a running instance of an application. You may casually refer
    to this as "the application" but we refer to it as an Assembly because
    most cloud applications are actually a system of multiple service
    instances that make up a system. For example, a three-tier web application
    may have a load balancer component, a group of application servers, and a
    database server all represented as Component resources that make up an
    Assembly resource. An Assembly resource has at least one Component resource
    associated with it.
    """

    uri = common_types.Uri
    "Uri to the Assembly"

    name = wtypes.text
    "Name of the Assembly"

    description = wtypes.text
    "Description of the Assembly"

    @classmethod
    def sample(cls):
        return cls(uri='http://localhost/v1/assemblies/x4',
                   name='database',
                   description='A mysql database')


class AssemblyController(rest.RestController):
    """Manages operations on a single assembly.
    """

    def __init__(self, assembly_id):
        pecan.request.context['assembly_id'] = assembly_id
        self._id = assembly_id

    @wsme_pecan.wsexpose(Assembly, wtypes.text)
    def get(self):
        """Return this assembly."""
        error = _("Not implemented")
        pecan.response.translatable_error = error
        raise wsme.exc.ClientSideError(unicode(error))

    @wsme_pecan.wsexpose(Assembly, wtypes.text, body=Assembly)
    def put(self, data):
        """Modify this assembly."""
        error = _("Not implemented")
        pecan.response.translatable_error = error
        raise wsme.exc.ClientSideError(unicode(error))

    @wsme_pecan.wsexpose(None, wtypes.text, status_code=204)
    def delete(self):
        """Delete this assembly."""
        error = _("Not implemented")
        pecan.response.translatable_error = error
        raise wsme.exc.ClientSideError(unicode(error))


class AssembliesController(rest.RestController):
    """Manages operations on the assemblies collection."""

    @pecan.expose()
    def _lookup(self, assembly_id, *remainder):
        if remainder and not remainder[-1]:
            remainder = remainder[:-1]
        return AssemblyController(assembly_id), remainder

    @wsme_pecan.wsexpose(Assembly, body=Assembly, status_code=201)
    def post(self, data):
        """Create a new assembly."""
        error = _("Not implemented")
        pecan.response.translatable_error = error
        raise wsme.exc.ClientSideError(unicode(error))

    @wsme_pecan.wsexpose([Assembly])
    def get_all(self):
        """Return all assemblys, based on the query provided."""
        return []


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
        return cls(uri='http://localhost/v1/services/mysql',
                   name='mysql',
                   description='A mysql service',
                   tags='group=xyz',
                   readOnly=False)


class ServiceController(rest.RestController):
    """Manages operations on a single service.
    """

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
    """A summary of services returned on listing.
    """

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
        return cls(uri='http://localhost/v1/services',
                   type='services',
                   description='Collection of services',
                   serviceLinks=[common_types.Link(
                       href='http://localhost:9777/v1/services/y4',
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


class Platform(wtypes.Base):
    """Representation of a Platform.

    The Platform resource is the root level resource that refers
    to all the other resources owned by this tenant.
    """

    uri = common_types.Uri
    "Uri to the platform"

    name = wtypes.text
    "The name of the platform"

    description = wtypes.text
    "Description of the platform"

    implementationVersion = wtypes.text
    "Version of the platform"

    assemblies = [common_types.Link]
    "List of links to assemblies"

    services = [common_types.Link]
    "List of links to services"

    @classmethod
    def sample(cls):
        return cls(uri='http://localhost/v1',
                   name='solum',
                   description='solum native implementation',
                   implementationVersion='2014.1.1',
                   assemblies=[common_types.Link(
                       href='http://localhost:9777/v1/assemblies/x2',
                       targetName='x2')],
                   services=[common_types.Link(
                       href='http://localhost:9777/v1/services/y4',
                       targetName='y4')])


class Controller(object):
    """Version 1 API controller root."""

    assemblies = AssembliesController()
    services = ServicesController()

    @wsme_pecan.wsexpose(Platform)
    def index(self):
        host_url = '%s/%s' % (pecan.request.host_url, 'v1')
        return Platform(uri=host_url,
                        name='solum',
                        description='solum native implementation',
                        implementationVersion=version.version_string())
