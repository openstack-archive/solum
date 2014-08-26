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

from solum.api.controllers.camp.v1_1.datamodel import format as model
from solum.common import exception


uri_string = '%s/camp/v1_1/json_format/'
name_string = 'JSON'
description_string = "JavaScript Object Notation"
doc_string = 'http://www.ietf.org/rfc/rfc4627.txt'


class Controller():
    """CAMP v1.1 json_format controller."""

    @exception.wrap_wsme_controller_exception
    @wsme_pecan.wsexpose(model.Format)
    def index(self):
        return model.Format(uri=uri_string % pecan.request.host_url,
                            name=name_string,
                            type='format',
                            description=description_string,
                            mime_type='application/json',
                            version='RFC4627',
                            documentation=doc_string)
