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

from solum.api.controllers.camp.v1_1.datamodel import plans as model
from solum.api.controllers.camp.v1_1 import uris
from solum.api.controllers import common_types
from solum.api.handlers import plan_handler
from solum.common import exception


class PlansController(rest.RestController):
    """CAMP v1.1 plans controller."""

    @exception.wrap_wsme_controller_exception
    @wsme_pecan.wsexpose(model.Plans)
    def get(self):
        puri = uris.PLANS_URI_STR % pecan.request.host_url
        pdef_uri = uris.DEPLOY_PARAMS_URI % pecan.request.host_url
        desc = "Solum CAMP API plans collection resource."

        handler = plan_handler.PlanHandler(pecan.request.security_context)
        plan_objs = handler.get_all()
        p_links = []
        for m in plan_objs:
            p_links.append(common_types.Link(href=uris.PLAN_URI_STR %
                                             (pecan.request.host_url, m.uuid),
                                             target_name=m.name))

        # if there aren't any plans, avoid returning a resource with an
        # empty plan_links array
        if len(p_links) > 0:
            res = model.Plans(uri=puri,
                              name='Solum_CAMP_plans',
                              type='plans',
                              description=desc,
                              parameter_definitions_uri=pdef_uri,
                              plan_links=p_links)
        else:
            res = model.Plans(uri=puri,
                              name='Solum_CAMP_plans',
                              type='plans',
                              description=desc,
                              parameter_definitions_uri=pdef_uri)
        return res
