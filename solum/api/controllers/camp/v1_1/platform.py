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

from solum.api.controllers.camp import platform_endpoints as pe
from solum.api.controllers.camp.v1_1.datamodel import platform as model
from solum.api.controllers.camp.v1_1 import uris
from solum.common import exception

uri_string = '%s/camp/v1_1/platform'
description_string = "Solum CAMP API platform resource for CAMP v1.1."


class PlatformController(rest.RestController):
    """CAMP v1.1 platform controller."""

    @exception.wrap_wsme_controller_exception
    @wsme_pecan.wsexpose(model.Platform)
    def get(self):
        host_url = pecan.request.application_url.rstrip('/')
        return model.Platform(uri=uri_string % host_url,
                              name='Solum_CAMP_v1_1_platform',
                              type='platform',
                              description=description_string,
                              supported_formats_uri=uris.FORMATS_URI_STR %
                              host_url,
                              extensions_uri=uris.EXTNS_URI_STR %
                              host_url,
                              type_definitions_uri=uris.TYPE_DEFS_URI_STR %
                              host_url,
                              platform_endpoints_uri=pe.URI_STRING %
                              host_url,
                              specification_version='CAMP 1.1',
                              implementation_version='Solum CAMP 1.1',
                              assemblies_uri=uris.ASSEMS_URI_STR %
                              host_url,
                              services_uri=uris.SERVS_URI_STR %
                              host_url,
                              plans_uri=uris.PLANS_URI_STR %
                              host_url)
