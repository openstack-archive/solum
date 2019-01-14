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

from solum.api.controllers.camp.v1_1.datamodel import services as model
from solum.api.controllers.camp.v1_1 import uris
from solum.api.controllers import common_types
from solum.api.handlers import service_handler
from solum.common import exception


class ServicesController(rest.RestController):
    """CAMP v1.1 services controller."""

    @exception.wrap_wsme_controller_exception
    @wsme_pecan.wsexpose(model.Services)
    def get(self):
        host_url = pecan.request.application_url.rstrip('/')
        suri = uris.SERVS_URI_STR % host_url
        desc = "Solum CAMP API services collection resource."

        handlr = service_handler.ServiceHandler(pecan.request.security_context)
        service_objs = handlr.get_all()
        s_links = []
        for m in service_objs:
            s_links.append(common_types.Link(href=uris.SERV_URI_STR %
                                             (host_url, m.uuid),
                                             target_name=m.name))

        # if there aren't any services, avoid returning a resource with an
        # empty service_links array
        if len(s_links) > 0:
            res = model.Services(uri=suri,
                                 name='Solum_CAMP_services',
                                 type='services',
                                 description=desc,
                                 service_links=s_links)
        else:
            res = model.Services(uri=suri,
                                 name='Solum_CAMP_services',
                                 type='services',
                                 description=desc)
        return res
