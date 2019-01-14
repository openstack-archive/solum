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
from wsme import types as wtypes
import wsmeext.pecan as wsme_pecan

from solum.api.controllers.v1.datamodel import operation
from solum.api.handlers import operation_handler
from solum.common import exception
from solum.common import policy
from solum import objects


class OperationController(rest.RestController):
    """Manages operations on a single operation."""

    def __init__(self, operation_id):
        super(OperationController, self).__init__()
        self._id = operation_id

    @exception.wrap_wsme_pecan_controller_exception
    @wsme_pecan.wsexpose(operation.Operation, wtypes.text)
    def get(self):
        """Return this operation."""
        policy.check('show_operation',
                     pecan.request.security_context)
        handler = operation_handler.OperationHandler(
            pecan.request.security_context)
        host_url = pecan.request.application_url.rstrip('/')
        return operation.Operation.from_db_model(handler.get(self._id),
                                                 host_url)

    @exception.wrap_wsme_pecan_controller_exception
    @wsme_pecan.wsexpose(operation.Operation, wtypes.text,
                         body=operation.Operation)
    def put(self, data):
        """Modify this operation."""
        policy.check('update_operation',
                     pecan.request.security_context)
        handler = operation_handler.OperationHandler(
            pecan.request.security_context)
        res = handler.update(self._id,
                             data.as_dict(objects.registry.Operation))
        host_url = pecan.request.application_url.rstrip('/')
        return operation.Operation.from_db_model(res, host_url)

    @exception.wrap_wsme_pecan_controller_exception
    @wsme_pecan.wsexpose(status_code=204)
    def delete(self):
        """Delete this operation."""
        policy.check('delete_operation',
                     pecan.request.security_context)
        handler = operation_handler.OperationHandler(
            pecan.request.security_context)
        handler.delete(self._id)


class OperationsController(rest.RestController):
    """Manages operations on the operations collection."""

    @pecan.expose()
    def _lookup(self, operation_id, *remainder):
        if remainder and not remainder[-1]:
            remainder = remainder[:-1]
        return OperationController(operation_id), remainder

    @exception.wrap_wsme_pecan_controller_exception
    @wsme_pecan.wsexpose(operation.Operation, body=operation.Operation,
                         status_code=201)
    def post(self, data):
        """Create a new operation."""
        policy.check('create_operation',
                     pecan.request.security_context)
        handler = operation_handler.OperationHandler(
            pecan.request.security_context)
        host_url = pecan.request.application_url.rstrip('/')
        return operation.Operation.from_db_model(handler.create(
            data.as_dict(objects.registry.Operation)), host_url)

    @exception.wrap_wsme_pecan_controller_exception
    @wsme_pecan.wsexpose([operation.Operation])
    def get_all(self):
        """Return all operations, based on the query provided."""
        policy.check('get_operations',
                     pecan.request.security_context)
        handler = operation_handler.OperationHandler(
            pecan.request.security_context)
        host_url = pecan.request.application_url.rstrip('/')
        return [operation.Operation.from_db_model(obj, host_url)
                for obj in handler.get_all()]
