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

from solum.api.controllers import common_types
from solum.api.controllers.v1.datamodel import component
from solum.api.controllers.v1.datamodel import operation
from solum.api.controllers.v1.datamodel import sensor
from solum.api.controllers.v1.datamodel import types as api_types


class Assembly(api_types.Base):
    """Representation of an Assembly.

    The Assembly resource represents a group of components that make
    up a running instance of an application. You may casually refer
    to this as "the application" but we refer to it as an Assembly because
    most cloud applications are actually a system of multiple service
    instances that make up a system. For example, a three-tier web
    application may have a load balancer component, a group of application
    servers, and a database server all represented as Component resources
    that make up an Assembly resource. An Assembly resource has at least
    one Component resource associated with it.
    """

    plan_uri = common_types.Uri
    """The URI to the plan to be used to create this assembly."""

    components = [component.Component]
    """Components that belong to the assembly."""

    operations = [operation.Operation]
    """Operations that belong to the assembly."""

    sensors = [sensor.Sensor]
    """Sensors that belong to the assembly."""

    @classmethod
    def sample(cls):
        return cls(uri='http://example.com/v1/assemblies/x4',
                   name='database',
                   type='assembly',
                   plan_uri='http://example.com/v1/plans/45-09',
                   tags=['small'],
                   project_id='1dae5a09ef2b4d8cbf3594b0eb4f6b94',
                   user_id='55f41cf46df74320b9486a35f5d28a11',
                   description='A mysql database',
                   components=[],
                   operations=[],
                   sensors=[])
