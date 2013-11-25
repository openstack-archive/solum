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
        return cls(uri='http://example.com/v1/operations/resume',
                   name='resume',
                   description='A resume operation',
                   operationLinks=[common_types.Link(
                               href='http://example.com:9777/v1/operations/x2',
                               targetName='x2')])


class OperationController(rest.RestController):
    """Manages operations on a single operation."""

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
    """A collection of operations returned on listing."""

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
        return cls(uri='http://example.com/v1/operations',
                   operationLinks=[common_types.Link(
                       href='http://example.com:9777/v1/operations/y4',
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
