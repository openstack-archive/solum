# Copyright 2014 - Rackspace Hosting
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
from wsme import types as wtypes
import wsmeext.pecan as wsme_pecan

from solum.api.controllers import common_types
from solum.builder.controllers.v1 import image


class V1Base(wtypes.Base):
    """List the V1 Image Controller resources."""

    images_uri = common_types.Uri
    "URI to images."


class Controller(object):
    """Version 1 API controller root."""

    images = image.ImagesController()

    @wsme_pecan.wsexpose(V1Base)
    def index(self):
        host_url = '%s/%s' % (pecan.request.host_url, 'v1')
        return V1Base(images_uri='%s/images' % host_url)
