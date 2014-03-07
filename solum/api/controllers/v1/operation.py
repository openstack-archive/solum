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

from solum.api.controllers.v1.datamodel import operation
from solum.api.handlers import operation_handler
from solum.common import exception
from solum.openstack.common.gettextutils import _


class OperationController(rest.RestController):
    """Manages operations on a single operation."""

    def __init__(self, operation_id):
        super(OperationController, self).__init__()
        self._id = operation_id

    @exception.wrap_controller_exception
    @wsme_pecan.wsexpose(operation.Operation, wtypes.text)
    def get(self):
        """Return this operation."""
        handler = operation_handler.OperationHandler(
            pecan.request.security_context)
        return handler.get(self._id)

    @wsme_pecan.wsexpose(operation.Operation, wtypes.text,
                         body=operation.Operation)
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

    @wsme_pecan.wsexpose(operation.Operation, body=operation.Operation,
                         status_code=201)
    def post(self, data):
        """Create a new operation."""
        error = _("Not implemented")
        pecan.response.translatable_error = error
        raise wsme.exc.ClientSideError(six.text_type(error))

    @exception.wrap_controller_exception
    @wsme_pecan.wsexpose([operation.Operation])
    def get_all(self):
        """Return all operations, based on the query provided."""
        handler = operation_handler.OperationHandler(
            pecan.request.security_context)
        return handler.get_all()
