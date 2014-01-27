# Copyright 2014 - Rackspace
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

from solum.api.controllers.v1.datamodel import types as api_types


class Service(api_types.Base):
    """The Service resource represents a networked service.

    You may create Component resources that refer to
    Service resources. A Component represents an instance of a Service.
    Your application connects to such a Component using a network protocol.
    For example, the Platform may offer a default Service named "mysql".
    You may create multiple Component resources that reference different
    instances of the "mysql" service. Each Component may be a multi-tenant
    instance of a MySQL database (perhaps a logical database) service offered
    by the Platform for a given Assembly.
    """

    read_only = bool
    """The service is read only when this value is true."""

    service_type = wtypes.text
    """Type of service. Example: language_pack or db::mysql"""

    @classmethod
    def sample(cls):
        return cls(uri='http://example.com/v1/language_packs/java1.4',
                   name='language-pack',
                   type='service',
                   service_type='language_pack',
                   description='A language pack service',
                   project_id='1dae5a09ef2b4d8cbf3594b0eb4f6b94',
                   user_id='55f41cf46df74320b9486a35f5d28a11',
                   tags=['group_xyz'],
                   read_only=False)

    @classmethod
    def sample1(cls):
        return cls(uri='http://example.com/v1/database/mysql',
                   name='database',
                   type='service',
                   service_type='db::mysql',
                   description='A mysql service',
                   project_id='1dae5a09ef2b4d8cbf3594b0eb4f6b94',
                   user_id='55f41cf46df74320b9486a35f5d28a11',
                   tags=['group_xyz'],
                   read_only=False)
