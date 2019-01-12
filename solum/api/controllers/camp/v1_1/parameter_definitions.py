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
from pecan import core
from pecan import rest
from wsme import types as wtypes
import wsmeext.pecan as wsme_pecan

from solum.api.controllers.camp.v1_1.datamodel import (parameter_definitions
                                                       as model)
from solum.api.handlers.camp import parameter_definitions_handler
from solum.common import exception


class ParamsDefController(rest.RestController):
    """Manages operations on a singular parameter_definitions resource."""

    def __init__(self, param_defs_name):
        super(ParamsDefController, self).__init__()
        self._id = param_defs_name

    @exception.wrap_wsme_controller_exception
    @wsme_pecan.wsexpose(model.ParameterDefinitions)
    def get(self):
        """Return the appropriate parameter_definitions resource."""
        handler = (parameter_definitions_handler.
                   ParameterDefinitionsHandler(pecan.request.security_context))
        raw_defs = handler.get(self._id)
        if not raw_defs:
            core.abort(404,
                       '%s is not a parameter_definitions collection' %
                       self._id)
        host_url = pecan.request.application_url.rstrip('/')
        return raw_defs.fix_uris(host_url)


class ParameterDefinitionsController(rest.RestController):
    """Manages operations on CAMP's parameter_definitions resources."""

#    @pecan.expose()
#    def _lookup(self, param_defs_name, *remainder):
#        if remainder and not remainder[-1]:
#            remainder = remainder[:-1]
#        return ParamsDefController(param_defs_name), remainder

    @exception.wrap_wsme_controller_exception
    @wsme_pecan.wsexpose(model.ParameterDefinitions, wtypes.text)
    def get_one(self, param_defs_name):
        """Return the appropriate format resource."""
        handler = (parameter_definitions_handler.
                   ParameterDefinitionsHandler(pecan.request.security_context))
        raw_defs = handler.get(param_defs_name)
        if not raw_defs:
            core.abort(404,
                       '%s is not a parameter_definitions collection' %
                       param_defs_name)
        host_url = pecan.request.application_url.rstrip('/')
        return raw_defs.fix_uris(host_url)
