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
from solum.api.controllers.v1 import app
from solum.api.controllers.v1 import assembly
from solum.api.controllers.v1 import component
from solum.api.controllers.v1.datamodel import types as api_types
from solum.api.controllers.v1 import extension
from solum.api.controllers.v1 import infrastructure
from solum.api.controllers.v1 import language_pack
from solum.api.controllers.v1 import operation
from solum.api.controllers.v1 import pipeline
from solum.api.controllers.v1 import plan
from solum.api.controllers.v1 import sensor
from solum.api.controllers.v1 import service
from solum.api.controllers.v1 import trigger
from solum.common import exception
from solum import version


class Platform(api_types.Base):
    """Representation of a Platform.

    The Platform resource is the root level resource that refers
    to all the other resources owned by this tenant.
    """

    implementation_version = wtypes.text
    "Version of the platform."

    plans_uri = common_types.Uri
    "URI to plans."

    assemblies_uri = common_types.Uri
    "URI to assemblies."

    services_uri = common_types.Uri
    "URI to services."

    components_uri = common_types.Uri
    "URI to components."

    extensions_uri = common_types.Uri
    "URI to extensions."

    operations_uri = common_types.Uri
    "URI to operations."

    sensors_uri = common_types.Uri
    "URI to sensors."

    language_packs_uri = common_types.Uri
    "URI to language packs."

    pipelines_uri = common_types.Uri
    "URI to pipelines."

    triggers_uri = common_types.Uri
    "URI to triggers."

    infrastructure_uri = common_types.Uri
    "URI to infrastructure."

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
                   plans_uri='http://example.com:9777/v1/plans',
                   assemblies_uri='http://example.com:9777/v1/assemblies',
                   services_uri='http://example.com:9777/v1/services',
                   components_uri='http://example.com:9777/v1/components',
                   extensions_uri='http://example.com:9777/v1/extensions',
                   operations_uri='http://example.com:9777/v1/operations',
                   sensors_uri='http://example.com:9777/v1/sensors',
                   language_packs_uri=(
                       'http://example.com:9777/v1/language_packs'),
                   pipelines_uri='http://example.com:9777/v1/pipelines',
                   triggers_uri='http://example.com:9777/v1/triggers',
                   infrastructure_uri=(
                       'http://example.com:9777/v1/infrastructure'))


class Controller(object):
    """Version 1 API controller root."""

    plans = plan.PlansController()
    apps = app.AppsController()
    assemblies = assembly.AssembliesController()
    services = service.ServicesController()
    components = component.ComponentsController()
    extensions = extension.ExtensionsController()
    operations = operation.OperationsController()
    sensors = sensor.SensorsController()
    language_packs = language_pack.LanguagePacksController()
    pipelines = pipeline.PipelinesController()
    triggers = trigger.TriggerController()
    infrastructure = infrastructure.InfrastructureController()

    @exception.wrap_wsme_pecan_controller_exception
    @wsme_pecan.wsexpose(Platform)
    def index(self):
        base_url = pecan.request.application_url.rstrip('/')
        host_url = '%s/%s' % (base_url, 'v1')
        return Platform(uri=host_url,
                        name='solum',
                        type='platform',
                        description='solum native implementation',
                        implementation_version=version.version_string(),
                        plans_uri='%s/plans' % host_url,
                        apps_uri='%s/apps' % host_url,
                        assemblies_uri='%s/assemblies' % host_url,
                        services_uri='%s/services' % host_url,
                        components_uri='%s/components' % host_url,
                        extensions_uri='%s/extensions' % host_url,
                        operations_uri='%s/operations' % host_url,
                        sensors_uri='%s/sensors' % host_url,
                        language_packs_uri='%s/language_packs' % host_url,
                        pipelines_uri='%s/pipelines' % host_url,
                        triggers_uri='%s/triggers' % host_url,
                        infrastructure_uri='%s/infrastructure' % host_url)
