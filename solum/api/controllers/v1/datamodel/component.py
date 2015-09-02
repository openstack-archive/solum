# Copyright 2013 - Rackspace
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
from wsme import types as wtypes

from solum.api.controllers import common_types
from solum.api.controllers.v1.datamodel import operation
from solum.api.controllers.v1.datamodel import sensor
from solum.api.controllers.v1.datamodel import service
from solum.api.controllers.v1.datamodel import types as api_types


class Component(api_types.Base):
    """The Component resource represents one part of an Assembly.

    For example, an instance of a database service may be a
    Component. A Component resource may also represent a static artifact, such
    as an archive file that contains data for initializing your application.
    An Assembly may have different components that represent different
    processes that run. For example, you may have one Component that represents
    an API service process, and another that represents a web UI process that
    consumes that API service. The simplest case is when an Assembly has only
    one component. For example, your component may be named "PHP" and refers to
    the PHP Service offered by the platform for running a PHP application.
    """

    assembly_uuid = wtypes.text
    """"The uuid of the assembly that this component belongs in."""

    services = [service.Service]
    """Services that belong to the component."""

    operations = [operation.Operation]
    """Operations that belong to the component."""

    sensors = [sensor.Sensor]
    """Sensors that belong to the component."""

    abbreviated = bool
    """Boolean value indicating if this components has nested components at
    more than one level of depth."""

    components_ids = [wtypes.text]
    """IDs of nested component of the component."""

    resource_uri = common_types.Uri
    """Remote resource URI of the component."""

    plan_uri = common_types.Uri
    """URI of Plan of which the component is a part."""

    component_type = wtypes.text
    """Type of component e.g. heat_stack."""

    heat_stack_id = wtypes.text
    """Unique identifier of the Heat Stack."""

    @classmethod
    def sample(cls):
        return cls(uri='http://example.com/v1/components/php-web-app',
                   name='php-web-app',
                   type='component',
                   component_type='heat_stack',
                   description='A php web application component',
                   tags=['group_xyz'],
                   project_id='1dae5a09ef2b4d8cbf3594b0eb4f6b94',
                   user_id='55f41cf46df74320b9486a35f5d28a11',
                   assembly_id='b3e0d79c698ea7b1561075bcfbbd2206a23d19b9',
                   heat_stack_id='4c712026-dcd5-4664-90b8-0915494c1332',
                   abbreviated=True,
                   components_ids=[],
                   services=[],
                   operations=[],
                   sensors=[])
