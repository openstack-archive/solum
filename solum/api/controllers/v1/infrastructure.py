# Copyright 2014 - Numergy
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
import wsmeext.pecan as wsme_pecan

from solum.api.controllers.v1.datamodel import infrastructure
from solum.api.handlers import infrastructure_handler
from solum.common import exception
from solum import objects


class InfrastructureStackController(rest.RestController):
    """Manages operations on a single stack."""

    def __init__(self, stack_id):
        super(InfrastructureStackController, self).__init__()
        self._id = stack_id

    @exception.wrap_wsme_pecan_controller_exception
    @wsme_pecan.wsexpose(infrastructure.InfrastructureStack)
    def get(self):
        """Return this stack."""
        handler = infrastructure_handler.InfrastructureStackHandler(
            pecan.request.security_context)
        host_url = pecan.request.application_url.rstrip('/')
        return infrastructure.InfrastructureStack.from_db_model(
            handler.get(self._id), host_url)

    @exception.wrap_wsme_pecan_controller_exception
    @wsme_pecan.wsexpose(infrastructure.InfrastructureStack,
                         body=infrastructure.InfrastructureStack)
    def put(self, data):
        """Modify this stack."""
        handler = infrastructure_handler.InfrastructureStackHandler(
            pecan.request.security_context)
        res = handler.update(self._id,
                             data.as_dict(
                                 objects.registry.InfrastructureStack))
        host_url = pecan.request.application_url.rstrip('/')
        return infrastructure.InfrastructureStack.from_db_model(
            res, host_url)

    @exception.wrap_wsme_pecan_controller_exception
    @wsme_pecan.wsexpose(status_code=204)
    def delete(self):
        """Delete this stack."""
        handler = infrastructure_handler.InfrastructureStackHandler(
            pecan.request.security_context)
        return handler.delete(self._id)


class InfrastructureStacksController(rest.RestController):
    """Manages operations on the stacks collection."""

    @pecan.expose()
    def _lookup(self, stack_id, *remainder):
        if remainder and not remainder[-1]:
            remainder = remainder[:-1]
        return InfrastructureStackController(stack_id), remainder

    @exception.wrap_wsme_pecan_controller_exception
    @wsme_pecan.wsexpose(infrastructure.InfrastructureStack,
                         body=infrastructure.InfrastructureStack,
                         status_code=201)
    def post(self, data):
        """Create a new stack."""
        handler = infrastructure_handler.InfrastructureStackHandler(
            pecan.request.security_context)
        host_url = pecan.request.application_url.rstrip('/')
        return infrastructure.InfrastructureStack.from_db_model(
            handler.create(data.as_dict(objects.registry.InfrastructureStack)),
            host_url)

    @exception.wrap_wsme_pecan_controller_exception
    @wsme_pecan.wsexpose([infrastructure.InfrastructureStack])
    def get_all(self):
        """Return all stacks, based on the query provided."""
        handler = infrastructure_handler.InfrastructureStackHandler(
            pecan.request.security_context)
        host_url = pecan.request.application_url.rstrip('/')
        return [infrastructure.InfrastructureStack.from_db_model(
            assm, host_url) for assm in handler.get_all()]


class InfrastructureController(rest.RestController):
    """Infrastructure root controller."""

    stacks = InfrastructureStacksController()

    @exception.wrap_wsme_pecan_controller_exception
    @wsme_pecan.wsexpose(infrastructure.Infrastructure)
    def index(self):
        base_url = pecan.request.application_url.rstrip('/')
        host_url = '%s/%s' % (base_url, 'v1')
        return infrastructure.Infrastructure(
            uri=host_url,
            name='solum',
            type='infrastructure',
            description='solum infrastructure endpoint',
            stacks_uri='%s/infrastructure/stacks' % host_url)
