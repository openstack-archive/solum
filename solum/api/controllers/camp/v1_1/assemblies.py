# -*- coding: utf-8 -*-
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

from solum.api.controllers.camp.v1_1.datamodel import assemblies as model
from solum.api.controllers.camp.v1_1 import uris
from solum.api.controllers import common_types
from solum.api.handlers import assembly_handler
from solum.common import exception


class AssembliesController(rest.RestController):
    """CAMP v1.1 assemblies controller."""

    @exception.wrap_wsme_controller_exception
    @wsme_pecan.wsexpose(model.Assemblies)
    def get(self):
        auri = uris.ASSEMS_URI_STR % pecan.request.host_url
        pdef_uri = uris.DEPLOY_PARAMS_URI % pecan.request.host_url
        desc = "Solum CAMP API assemblies collection resource"

        handlr = (assembly_handler.
                  AssemblyHandler(pecan.request.security_context))
        asem_objs = handlr.get_all()
        a_links = []
        for m in asem_objs:
            a_links.append(common_types.Link(href=uris.ASSEM_URI_STR %
                                             (pecan.request.host_url, m.uuid),
                                             target_name=m.name))

        # if there aren't any assemblies, avoid returning a resource with an
        # empty assembly_links array
        if len(a_links) > 0:
            res = model.Assemblies(uri=auri,
                                   name='Solum_CAMP_assemblies',
                                   type='assemblies',
                                   description=desc,
                                   parameter_definitions_uri=pdef_uri,
                                   assembly_links=a_links)
        else:
            res = model.Assemblies(uri=auri,
                                   name='Solum_CAMP_assemblies',
                                   type='assemblies',
                                   description=desc,
                                   parameter_definitions_uri=pdef_uri)

        return res
