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

from solum.api.controllers.camp.v1_1.datamodel import type_definitions as model
from solum.api.controllers.camp.v1_1 import uris
from solum.api.controllers import common_types
from solum.api.handlers.camp import type_definition_handler
from solum.common import exception


DESCRIPTION_STRING = "Solum CAMP API type_definitions collection resource."


class TypeDefinitionsController(rest.RestController):
    """CAMP v1.1 type_definitions controller."""

    @exception.wrap_wsme_controller_exception
    @wsme_pecan.wsexpose(model.TypeDefinition, wtypes.text)
    def get_one(self, type_def_name):
        handler = (type_definition_handler.
                   TypeDefinitionHandler(pecan.request.security_context))
        raw_def = handler.get(type_def_name)
        if not raw_def:
            core.abort(404,
                       '%s is not a type_definition' %
                       type_def_name)
        host_url = pecan.request.application_url.rstrip('/')
        return raw_def.fix_uris(host_url)

    @exception.wrap_wsme_controller_exception
    @wsme_pecan.wsexpose(model.TypeDefinitions)
    def get(self):
        links = []
        handler = (type_definition_handler.
                   TypeDefinitionHandler(pecan.request.security_context))
        def_list = handler.get_all()

        host_url = pecan.request.application_url.rstrip('/')
        for tdef in def_list:
            links.append(common_types.Link(href=uris.TYPE_DEF_URI_STR %
                                           (host_url, tdef.uri),
                                           target_name=tdef.name))

        return model.TypeDefinitions(uri=uris.TYPE_DEFS_URI_STR % host_url,
                                     name='Solum_CAMP_type_definitions',
                                     type='type_definitions',
                                     description=DESCRIPTION_STRING,
                                     type_definition_links=links)
