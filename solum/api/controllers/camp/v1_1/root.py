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

from solum.api.controllers.camp.v1_1 import assemblies
from solum.api.controllers.camp.v1_1 import extensions
from solum.api.controllers.camp.v1_1 import formats
from solum.api.controllers.camp.v1_1 import json_format
from solum.api.controllers.camp.v1_1 import parameter_definitions
from solum.api.controllers.camp.v1_1 import plans
from solum.api.controllers.camp.v1_1 import platform
from solum.api.controllers.camp.v1_1 import services
from solum.api.controllers.camp.v1_1 import type_definitions


class Controller(object):
    """CAMP API version 1.1 controller root."""

    assemblies = assemblies.Controller()
    extensions = extensions.Controller()
    formats = formats.Controller()
    json_format = json_format.Controller()
    plans = plans.Controller()
    platform = platform.Controller()
    services = services.Controller()
    type_definitions = type_definitions.Controller()
    parameter_definitions = (parameter_definitions.
                             ParameterDefinitionsController())
