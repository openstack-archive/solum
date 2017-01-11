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

from pecan import rest

from solum.api.controllers.camp.v1_1 import assemblies
from solum.api.controllers.camp.v1_1 import attribute_definitions
from solum.api.controllers.camp.v1_1 import extensions
from solum.api.controllers.camp.v1_1 import formats
from solum.api.controllers.camp.v1_1 import parameter_definitions
from solum.api.controllers.camp.v1_1 import plans
from solum.api.controllers.camp.v1_1 import platform
from solum.api.controllers.camp.v1_1 import services
from solum.api.controllers.camp.v1_1 import type_definitions


class Controller(rest.RestController):
    """CAMP API version 1.1 controller root."""

    assemblies = assemblies.AssembliesController()
    attribute_definitions = (attribute_definitions.
                             AttributeDefinitionsController())
    extensions = extensions.ExtensionsController()
    formats = formats.FormatsController()
    parameter_definitions = (parameter_definitions.
                             ParameterDefinitionsController())
    plans = plans.PlansController()
    platform = platform.PlatformController()
    services = services.ServicesController()
    type_definitions = type_definitions.TypeDefinitionsController()
