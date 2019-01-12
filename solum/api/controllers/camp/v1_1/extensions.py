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

from solum.api.controllers.camp.v1_1.datamodel import extensions as model
from solum.api.controllers.camp.v1_1 import uris
from solum.api.controllers import common_types
from solum.api.handlers import extension_handler
from solum.common import exception


uri_string = '%s/camp/v1_1/extensions/'
description_string = "Solum CAMP API extensions collection resource."


class ExtensionsController(rest.RestController):
    """CAMP v1.1 extensions controller."""

    @exception.wrap_wsme_controller_exception
    @wsme_pecan.wsexpose(model.Extensions)
    def get(self):
        host_url = pecan.request.application_url.rstrip('/')
        euri = uris.EXTNS_URI_STR % host_url
        desc = "Solum CAMP API extensions collection resource."

        handlr = (extension_handler.
                  ExtensionHandler(pecan.request.security_context))
        ext_objs = handlr.get_all()
        e_links = []
        for m in ext_objs:
            e_links.append(common_types.Link(href=uris.EXTN_URI_STR %
                                             (host_url, m.uuid),
                                             target_name=m.name))

        # if there aren't any extensions, avoid returning a resource with an
        # empty extension_links array
        if len(e_links) > 0:
            res = model.Extensions(uri=euri,
                                   name="Solum_CAMP_extensions",
                                   type='extensions',
                                   description=desc,
                                   extension_links=e_links)
        else:
            res = model.Extensions(uri=euri,
                                   name="Solum_CAMP_extensions",
                                   type='extensions',
                                   description=desc)
        return res
