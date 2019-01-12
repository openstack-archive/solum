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

from solum.api.controllers.camp.v1_1.datamodel import (attribute_definitions
                                                       as model)
from solum.api.handlers.camp import attribute_definition_handler
from solum.common import exception


class AttributeDefinitionsController(rest.RestController):
    """CAMP v1.1 attribute_definitions controller."""

    @exception.wrap_wsme_controller_exception
    @wsme_pecan.wsexpose(model.AttributeDefinition, wtypes.text)
    def get_one(self, attr_def_name):
        handler = (attribute_definition_handler.
                   AttributeDefinitionHandler(pecan.request.security_context))
        raw_def = handler.get(attr_def_name)
        if not raw_def:
            core.abort(404,
                       '%s is not a attribute_definition' %
                       attr_def_name)
        host_url = pecan.request.application_url.rstrip('/')
        return raw_def.fix_uris(host_url)
