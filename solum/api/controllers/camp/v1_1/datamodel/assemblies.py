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

from solum.api.controllers import common_types
from solum.api.controllers.v1.datamodel import types as api_types


class Assemblies(api_types.Base):
    """CAMP v1.1 assemblies resource model."""

    assembly_links = [common_types.Link]
    """This attribute contains Links to the assembly resources that represent
     the applications deployed on this platform."""

    parameter_definitions_uri = common_types.Uri
    """The value of the parameter_definitions_uri attribute references a
     resource that contains links to parameter_definitions resources that
     describe the parameters accepted by this resource on an HTTP POST
     method."""

    def __init__(self, **kwds):
        super(Assemblies, self).__init__(**kwds)
