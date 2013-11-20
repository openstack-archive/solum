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
