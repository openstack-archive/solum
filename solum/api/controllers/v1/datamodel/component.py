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

    assembly_link = common_types.Link
    """Link to the assembly."""

    component_links = [common_types.Link]
    """List of links to the available components."""

    service_links = [common_types.Link]
    """List of links to the available services."""

    operations_uri = common_types.Uri
    """URI for the operations."""

    sensors_uri = common_types.Uri
    """URI for the sensors."""

    @classmethod
    def sample(cls):
        return cls(uri='http://example.com/v1/components/php-web-app',
                   name='php-web-app',
                   type='component',
                   description='A php web application component',
                   tags=['group_xyz'],
                   project_id='1dae5a09ef2b4d8cbf3594b0eb4f6b94',
                   user_id='55f41cf46df74320b9486a35f5d28a11',
                   assembly_link=common_types.Link(
                       href='http://example.com:9777/v1/assembly/a2',
                       target_name='a2'),
                   component_links=[common_types.Link(
                       href='http://example.com:9777/v1/components/x2',
                       target_name='x2')],
                   service_links=[common_types.Link(
                       href='http://example.com:9777/v1/services/s2',
                       target_name='s2')],
                   operations_uri='http://example.com:9777/v1/operations/o1',
                   sensors_uri='http://example.com:9777/v1/sensors/s1')
