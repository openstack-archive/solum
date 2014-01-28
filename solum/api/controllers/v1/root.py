# Copyright 2013 - Noorul Islam K M
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
from solum.api.controllers.v1 import assembly
from solum.api.controllers.v1 import component
from solum.api.controllers.v1.datamodel import types as api_types
from solum.api.controllers.v1 import extension
from solum.api.controllers.v1 import operation
from solum.api.controllers.v1 import sensor
from solum.api.controllers.v1 import service
from solum import version


class Platform(api_types.Base):
    """Representation of a Platform.

    The Platform resource is the root level resource that refers
    to all the other resources owned by this tenant.
    """

    implementation_version = wtypes.text
    "Version of the platform."

    assemblies_uri = common_types.Uri
    "URI to assemblies."

    services_uri = common_types.Uri
    "URI to services."

    components_uri = common_types.Uri
    "URI to components."

    extensions_uri = common_types.Uri
    "URI to extensions."

    @classmethod
    def sample(cls):
        return cls(uri='http://example.com/v1',
                   name='solum',
                   type='platform',
                   tags=['solid'],
                   project_id='1dae5a09ef2b4d8cbf3594b0eb4f6b94',
                   user_id='55f41cf46df74320b9486a35f5d28a11',
                   description='solum native implementation',
                   implementation_version='2014.1.1',
                   assemblies_uri='http://example.com:9777/v1/assemblies',
                   services_uri='http://example.com:9777/v1/services',
                   components_uri='http://example.com:9777/v1/components',
                   extensions_uri='http://example.com:9777/v1/extensions')


class Controller(object):
    """Version 1 API controller root."""

    assemblies = assembly.AssembliesController()
    services = service.ServicesController()
    components = component.ComponentsController()
    extensions = extension.ExtensionsController()
    operations = operation.OperationsController()
    sensors = sensor.SensorsController()

    @wsme_pecan.wsexpose(Platform)
    def index(self):
        host_url = '%s/%s' % (pecan.request.host_url, 'v1')
        return Platform(uri=host_url,
                        name='solum',
                        type='platform',
                        description='solum native implementation',
                        implementation_version=version.version_string(),
                        assemblies_uri='%s/assemblies' % host_url,
                        services_uri='%s/services' % host_url,
                        components_uri='%s/components' % host_url,
                        extensions_uri='%s/extensions' % host_url)
