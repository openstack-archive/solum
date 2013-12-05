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

from solum.api.controllers import common_types
from solum.api.controllers.v1 import types as api_types
from solum.openstack.common.gettextutils import _


class Operation(api_types.Base):
    """An Operation resource represents an operation or action available on a
    target resource. This is for defining actions that may change the state of
    the resource they are related to. For example, the API already provides
    ways to register, start, and stop your application (POST an Assembly to
    register+start, and DELETE an Assembly to stop) but Operations provide a
    way to extend the system to add your own actions such as "pause" and
    "resume", or "scale_up" and "scale_down".
    """

    documentation = common_types.Uri
    "Documentation URI for the operation."

    target_resource = common_types.Uri
    "Target resource URI to the operation."

    @classmethod
    def sample(cls):
        return cls(uri='http://example.com/v1/operations/resume',
                   name='resume',
                   type='operation',
                   tags=['small'],
                   description='A resume operation',
                   documentation='http://example.com/docs/resume_op',
                   target_resource='http://example.com/instances/uuid')


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
        raise wsme.exc.ClientSideError(six.text_type(error))

    @wsme_pecan.wsexpose(Operation, wtypes.text, body=Operation)
    def put(self, data):
        """Modify this operation."""
        error = _("Not implemented")
        pecan.response.translatable_error = error
        raise wsme.exc.ClientSideError(six.text_type(error))

    @wsme_pecan.wsexpose(None, wtypes.text, status_code=204)
    def delete(self):
        """Delete this operation."""
        error = _("Not implemented")
        pecan.response.translatable_error = error
        raise wsme.exc.ClientSideError(six.text_type(error))


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
        raise wsme.exc.ClientSideError(six.text_type(error))

    @wsme_pecan.wsexpose([Operation])
    def get_all(self):
        """Return all operations, based on the query provided."""
        return []
