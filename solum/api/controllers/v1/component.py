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

from solum.api.controllers.v1.datamodel import component
from solum.api.handlers import component_handler
from solum.common import exception
from solum.common import policy
from solum import objects


class ComponentController(rest.RestController):
    """Manages operations on a single component."""

    def __init__(self, component_id):
        super(ComponentController, self).__init__()
        self._id = component_id

    @exception.wrap_wsme_pecan_controller_exception
    @wsme_pecan.wsexpose(component.Component)
    def get(self):
        """Return this component."""
        policy.check('show_component',
                     pecan.request.security_context)
        handler = component_handler.ComponentHandler(
            pecan.request.security_context)
        host_url = pecan.request.application_url.rstrip('/')
        return component.Component.from_db_model(handler.get(self._id),
                                                 host_url)

    @exception.wrap_wsme_pecan_controller_exception
    @wsme_pecan.wsexpose(component.Component, body=component.Component)
    def put(self, data):
        """Modify this component."""
        policy.check('update_component',
                     pecan.request.security_context)
        handler = component_handler.ComponentHandler(
            pecan.request.security_context)
        res = handler.update(self._id,
                             data.as_dict(objects.registry.Component))
        host_url = pecan.request.application_url.rstrip('/')
        return component.Component.from_db_model(res, host_url)

    @exception.wrap_wsme_pecan_controller_exception
    @wsme_pecan.wsexpose(None, status_code=204)
    def delete(self):
        """Delete this component."""
        policy.check('delete_component',
                     pecan.request.security_context)
        handler = component_handler.ComponentHandler(
            pecan.request.security_context)
        return handler.delete(self._id)


class ComponentsController(rest.RestController):
    """Manages operations on the components collection."""

    @pecan.expose()
    def _lookup(self, component_id, *remainder):
        if remainder and not remainder[-1]:
            remainder = remainder[:-1]
        return ComponentController(component_id), remainder

    @exception.wrap_wsme_pecan_controller_exception
    @wsme_pecan.wsexpose(component.Component, body=component.Component,
                         status_code=201)
    def post(self, data):
        """Create a new component."""
        policy.check('create_component',
                     pecan.request.security_context)
        handler = component_handler.ComponentHandler(
            pecan.request.security_context)
        host_url = pecan.request.application_url.rstrip('/')
        return component.Component.from_db_model(
            handler.create(data.as_dict(objects.registry.Component)), host_url)

    @exception.wrap_wsme_pecan_controller_exception
    @wsme_pecan.wsexpose([component.Component])
    def get_all(self):
        """Return all components, based on the query provided."""
        policy.check('get_components',
                     pecan.request.security_context)
        handler = component_handler.ComponentHandler(
            pecan.request.security_context)
        host_url = pecan.request.application_url.rstrip('/')
        return [component.Component.from_db_model(ser, host_url)
                for ser in handler.get_all()]
