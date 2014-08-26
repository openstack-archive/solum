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

from solum.api.controllers.camp.datamodel import platform_endpoint as model
from solum.common import exception


uri_string = '%s/camp/camp_v1_1_endpoint/'
name_string = 'Solum_CAMP_v1_1_endpoint'
platform_uri_string = '%s/camp/v1_1/platform/'
description_string = "Solum CAMP v1.1 API platform_endpoint resource."


class Controller(object):
    """camp_v1_1_endpoint resource controller."""

    @exception.wrap_wsme_controller_exception
    @wsme_pecan.wsexpose(model.PlatformEndpoint)
    def index(self):
        return model.PlatformEndpoint(uri=uri_string % pecan.request.host_url,
                                      name=name_string,
                                      type='platform_endpoint',
                                      description=description_string,
                                      platform_uri=platform_uri_string %
                                      pecan.request.host_url,
                                      specification_version='CAMP 1.1',
                                      implementation_version='Solum CAMP 1.1',
                                      auth_scheme='KEYSTONE-2.0')
