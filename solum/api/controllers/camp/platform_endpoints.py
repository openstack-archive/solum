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
import wsmeext.pecan as wsme_pecan

from solum.api.controllers.camp import camp_v1_1_endpoint as endpoint
from solum.api.controllers.camp.datamodel import platform_endpoints as model
from solum.api.controllers import common_types
from solum.common import exception


uri_string = '%s/camp/platform_endpoints/'
description_string = "Solum CAMP API platform_endpoints resource."


class Controller(object):
    """platform_endpoints resource controller."""

    @exception.wrap_wsme_controller_exception
    @wsme_pecan.wsexpose(model.PlatformEndpoints)
    def index(self):
        links = [
            common_types.Link(href=endpoint.uri_string %
                              pecan.request.host_url,
                              target_name=endpoint.name_string)
        ]

        return model.PlatformEndpoints(uri=uri_string % pecan.request.host_url,
                                       name='Solum_CAMP_endpoints',
                                       type='platform_endpoints',
                                       description=description_string,
                                       platform_endpoint_links=links)
