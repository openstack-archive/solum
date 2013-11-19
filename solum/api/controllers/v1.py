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

import datetime
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


class Component(wtypes.Base):
    """The Component resource represents one part of an Assembly needed by your
    application.For example, an instance of a database service may be a
    Component. A Component resource may also represent a static artifact, such
    as an archive file that contains data for initializing your application.
    An Assembly may have different components that represent different
    processes that run. For example, you may have one Component that represents
    an API service process, and another that represents a web UI process that
    consumes that API service. This simplest case is when an Assembly has only
    one component. For examaple your component may be named "PHP" and refers to
    the PHP Service offered by the platform for running a PHP application.
    """

    uri = common_types.Uri
    "Uri to the component"

    name = wtypes.text
    "Name of the component"

    type = wtypes.text
    "Component type"

    description = wtypes.text
    "Description of the component"

    tags = [wtypes.text]
    "Tags for the component"

    assemblyLink = common_types.Link
    "Link to the assembly"

    componentLinks = [common_types.Link]
    "List of links to the available components"

    serviceLinks = [common_types.Link]
    "List of links to the available services"

    operationsUri = common_types.Uri
    "Uri to the operations"

    sensorsUri = common_types.Uri
    "Uri to the sensors"

    @classmethod
    def sample(cls):
        return cls(uri='http://localhost/v1/components/php',
                   name='php',
                   description='A php component',
                   tags='group=xyz',
                   assemblyLink=common_types.Link(
                       href='http://localhost:9777/v1/assembly/a2',
                       targetName='a2'),
                   componentLinks=common_types.Link(
                       href='http://localhost:9777/v1/components/x2',
                       targetName='x2'),
                   serviceLinks=common_types.Link(
                       href='http://localhost:9777/v1/services/s2',
                       targetName='s2'),
                   operationsUri='http://localhost:9777/v1/operations/o1',
                   sensorsUri='http://localhost:9777/v1/sensors/s1')


class ComponentController(rest.RestController):
    """Manages operations on a single component.
    """

    def __init__(self, component_id):
        pecan.request.context['component_id'] = component_id
        self._id = component_id

    @wsme_pecan.wsexpose(Component, wtypes.text)
    def get(self):
        """Return this component."""
        error = _("Not implemented")
        pecan.response.translatable_error = error
        raise wsme.exc.ClientSideError(unicode(error))

    @wsme_pecan.wsexpose(Component, wtypes.text, body=Component)
    def put(self, data):
        """Modify this component."""
        error = _("Not implemented")
        pecan.response.translatable_error = error
        raise wsme.exc.ClientSideError(unicode(error))

    @wsme_pecan.wsexpose(None, wtypes.text, status_code=204)
    def delete(self):
        """Delete this component."""
        error = _("Not implemented")
        pecan.response.translatable_error = error
        raise wsme.exc.ClientSideError(unicode(error))


class ComponentsController(rest.RestController):
    """Manages operations on the components collection."""

    @pecan.expose()
    def _lookup(self, component_id, *remainder):
        if remainder and not remainder[-1]:
            remainder = remainder[:-1]
        return ComponentController(component_id), remainder

    @wsme_pecan.wsexpose(Component, body=Component, status_code=201)
    def post(self, data):
        """Create a new component."""
        error = _("Not implemented")
        pecan.response.translatable_error = error
        raise wsme.exc.ClientSideError(unicode(error))

    @wsme_pecan.wsexpose([Component])
    def get_all(self):
        """Return all components, based on the query provided."""
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

    components = [common_types.Link]
    "List of links to the available components"

    extensions = [common_types.Link]
    "List of links to extensions"

    operations = [common_types.Link]
    "List of links to operations"

    sensors = [common_types.Link]
    "List of links to sensors"

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
                       targetName='y4')],
                   componentLinks=[common_types.Link(
                       href='http://localhost:9777/v1/components/x2',
                       targetName='x2')],
                   extensions=[common_types.Link(
                       href='http://localhost:9777/v1/extensions/z4',
                       targetName='z4')],
                   operations=[common_types.Link(
                       href='http://localhost:9777/v1/operations/o4',
                       targetName='o4')],
                   sensors=[common_types.Link(
                       href='http://localhost:9777/v1/sensors/s3',
                       targetName='s3')])


class Extension(wtypes.Base):
    """The Extension resource represents changes that the Provider has added
    onto a Platform in addition to the ones supplied by Solum by default.
    This may include additional protocol semantics, resource types,
    application lifecycle states, resource attributes, etc. Anything may be
    added, as long as it does not contradict the base functionality offered
    by Solum.
    """

    uri = common_types.Uri
    "Uri to the extension"

    name = wtypes.text
    "Name of the extension"

    type = wtypes.text
    "Extension type"

    description = wtypes.text
    "Description of the extension"

    version = wtypes.text
    "Version of the extension"

    documentation = common_types.Uri
    "Documentation uri to the extension"

    @classmethod
    def sample(cls):
        return cls(uri='http://localhost/v1/extensions/mysql',
                   name='mysql',
                   description='A mysql extension',
                   extensionLinks=[common_types.Link(
                               href='http://localhost:9777/v1/extensions/x2',
                               targetName='x2')])


class ExtensionController(rest.RestController):
    """Manages operations on a single extension.
    """

    def __init__(self, extension_id):
        pecan.request.context['extension_id'] = extension_id
        self._id = extension_id

    @wsme_pecan.wsexpose(Extension, wtypes.text)
    def get(self):
        """Return this extension."""
        error = _("Not implemented")
        pecan.response.translatable_error = error
        raise wsme.exc.ClientSideError(unicode(error))


class Extensions(wtypes.Base):
    """A collection of extensions returned on listing.
    """

    uri = common_types.Uri
    "Uri to the Extensions"

    name = wtypes.text
    "Name of the extension"

    type = wtypes.text
    "Extension type"

    description = wtypes.text
    "Description of the extension"

    extensionLinks = [common_types.Link]
    "List of links to the available extensions"

    @classmethod
    def sample(cls):
        return cls(uri='http://localhost/v1/extensions',
                   extensionLinks=[common_types.Link(
                       href='http://localhost:9777/v1/extensions/y4',
                       targetName='y4')])


class ExtensionsController(rest.RestController):
    """Manages operations on the extensions collection."""

    @pecan.expose()
    def _lookup(self, extension_id, *remainder):
        if remainder and not remainder[-1]:
            remainder = remainder[:-1]
        return ExtensionController(extension_id), remainder

    @wsme_pecan.wsexpose(Extensions)
    def get_all(self):
        """Return all extensions, based on the query provided."""
        host_url = '/'.join([pecan.request.host_url, 'v1', 'extensions'])
        return Extensions(uri=host_url,
                          type='extensions',
                          description='Collection of extensions',
                          extensionLinks=[])


class Operation(wtypes.Base):
    """An Operation resource represents an operation or action available on a
    target resource. This is for defining actions that may change the state of
    the resource they are related to. For example, the API already provides
    ways to register, start, and stop your application (POST an Assembly to
    register+start, and DELETE an Assembly to stop) but Operations provide a
    way to extend the system to add your own actions such as "pause" and
    "resume", or "scale_up" and "scale_down".
    """

    uri = common_types.Uri
    "Uri to the operation"

    name = wtypes.text
    "Name of the operation"

    type = wtypes.text
    "Operation type"

    description = wtypes.text
    "Description of the operation"

    documentation = common_types.Uri
    "Documentation uri for the operation"

    targetResource = common_types.Uri
    "Target resource uri to the operation"

    @classmethod
    def sample(cls):
        return cls(uri='http://localhost/v1/operations/resume',
                   name='resume',
                   description='A resume operation',
                   operationLinks=[common_types.Link(
                               href='http://localhost:9777/v1/operations/x2',
                               targetName='x2')])


class OperationController(rest.RestController):
    """Manages operations on a single operation.
    """

    def __init__(self, operation_id):
        pecan.request.context['operation_id'] = operation_id
        self._id = operation_id

    @wsme_pecan.wsexpose(Operation, wtypes.text)
    def get(self):
        """Return this operation."""
        error = _("Not implemented")
        pecan.response.translatable_error = error
        raise wsme.exc.ClientSideError(unicode(error))

    @wsme_pecan.wsexpose(Operation, wtypes.text, body=Operation)
    def put(self, data):
        """Modify this operation."""
        error = _("Not implemented")
        pecan.response.translatable_error = error
        raise wsme.exc.ClientSideError(unicode(error))

    @wsme_pecan.wsexpose(None, wtypes.text, status_code=204)
    def delete(self):
        """Delete this operation."""
        error = _("Not implemented")
        pecan.response.translatable_error = error
        raise wsme.exc.ClientSideError(unicode(error))


class Operations(wtypes.Base):
    """A collection of operations returned on listing.
    """

    uri = common_types.Uri
    "Uri to the Operations"

    name = wtypes.text
    "Name of the operation"

    type = wtypes.text
    "Operation type"

    description = wtypes.text
    "Description of the operation"

    targetResource = common_types.Uri
    "Target resource uri to the operation"

    operationLinks = [common_types.Link]
    "List of links to the available operations"

    @classmethod
    def sample(cls):
        return cls(uri='http://localhost/v1/operations',
                   operationLinks=[common_types.Link(
                       href='http://localhost:9777/v1/operations/y4',
                       targetName='y4')])


class OperationsController(rest.RestController):
    """Manages operations on the operations collection."""

    @pecan.expose()
    def _lookup(self, operation_id, *remainder):
        if remainder and not remainder[-1]:
            remainder = remainder[:-1]
        return OperationController(operation_id), remainder

    @wsme_pecan.wsexpose(Operation, body=Operation, status_code=201)
    def post(self, data):
        """Create a new operation."""
        error = _("Not implemented")
        pecan.response.translatable_error = error
        raise wsme.exc.ClientSideError(unicode(error))

    @wsme_pecan.wsexpose(Operations)
    def get_all(self):
        """Return all operations, based on the query provided."""
        host_url = '/'.join([pecan.request.host_url, 'v1', 'operations'])
        return Operations(uri=host_url,
                          type='operations',
                          description='Collection of operations',
                          operationLinks=[])


class Sensor(wtypes.Base):
    """A Sensor resource represents exactly one supported sensor on one or
    more resources. Sensor resources represent dynamic data about resources,
    such as metrics or state. Sensor resources are useful for exposing data
    that changes rapidly, or that may need to be fetched from a secondary
    system.
    """

    uri = common_types.Uri
    "Uri to the sensor"

    name = wtypes.text
    "Name of the sensor"

    type = wtypes.text
    "Sensor type"

    description = wtypes.text
    "Description of the sensor"

    documentation = common_types.Uri
    "Documentation uri for the sensor"

    targetResource = common_types.Uri
    "Target resource uri to the sensor"

    sensorType = wtypes.text
    "Sensor type"

    value = sensorType
    "Value of sensor"

    timestamp = datetime.datetime
    "Timestamp for Sensor"

    operationsUri = common_types.Uri
    "Operations uri for the sensor"

    @classmethod
    def sample(cls):
        return cls(uri='http://localhost/v1/sensors/hb',
                   name='hb',
                   description='A heartbeat sensor',
                   sensorLinks=[common_types.Link(
                               href='http://localhost:9777/v1/sensors/s2',
                               targetName='s2')])


class SensorController(rest.RestController):
    """Manages operations on a single sensor.
    """

    def __init__(self, sensor_id):
        pecan.request.context['sensor_id'] = sensor_id
        self._id = sensor_id

    @wsme_pecan.wsexpose(Sensor, wtypes.text)
    def get(self):
        """Return this sensor."""
        error = _("Not implemented")
        pecan.response.translatable_error = error
        raise wsme.exc.ClientSideError(unicode(error))

    @wsme_pecan.wsexpose(Sensor, wtypes.text, body=Sensor)
    def put(self, data):
        """Modify this sensor."""
        error = _("Not implemented")
        pecan.response.translatable_error = error
        raise wsme.exc.ClientSideError(unicode(error))

    @wsme_pecan.wsexpose(None, wtypes.text, status_code=204)
    def delete(self):
        """Delete this sensor."""
        error = _("Not implemented")
        pecan.response.translatable_error = error
        raise wsme.exc.ClientSideError(unicode(error))


class Sensors(wtypes.Base):
    """A collection of sensors returned on listing.
    """

    uri = common_types.Uri
    "Uri to the Sensors"

    name = wtypes.text
    "Name of the sensor"

    type = wtypes.text
    "Sensor type"

    description = wtypes.text
    "Description of the sensor"

    targetResource = common_types.Uri
    "Target resource uri to the sensor"

    sensorLinks = [common_types.Link]
    "List of links to the available sensors"

    @classmethod
    def sample(cls):
        return cls(uri='http://localhost/v1/sensors',
                   sensorLinks=[common_types.Link(
                       href='http://localhost:9777/v1/sensors/y4',
                       targetName='y4')])


class SensorsController(rest.RestController):
    """Manages operations on the sensors collection."""

    @pecan.expose()
    def _lookup(self, sensor_id, *remainder):
        if remainder and not remainder[-1]:
            remainder = remainder[:-1]
        return SensorController(sensor_id), remainder

    @wsme_pecan.wsexpose(Sensor, body=Sensor, status_code=201)
    def post(self, data):
        """Create a new sensor."""
        error = _("Not implemented")
        pecan.response.translatable_error = error
        raise wsme.exc.ClientSideError(unicode(error))

    @wsme_pecan.wsexpose(Sensors)
    def get_all(self):
        """Return all sensors, based on the query provided."""
        host_url = '/'.join([pecan.request.host_url, 'v1', 'sensors'])
        return Sensors(uri=host_url,
                       type='sensors',
                       description='Collection of sensors',
                       sensorLinks=[])


class Controller(object):
    """Version 1 API controller root."""

    assemblies = AssembliesController()
    services = ServicesController()
    components = ComponentsController()
    extensions = ExtensionsController()
    operations = OperationsController()
    sensors = SensorsController()

    @wsme_pecan.wsexpose(Platform)
    def index(self):
        host_url = '%s/%s' % (pecan.request.host_url, 'v1')
        return Platform(uri=host_url,
                        name='solum',
                        description='solum native implementation',
                        implementationVersion=version.version_string())
