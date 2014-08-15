# Copyright 2014 - Numergy
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
from solum.api.controllers.v1.datamodel import types as api_types


class Infrastructure(api_types.Base):
    """Description of an Infrastructure."""

    stacks_uri = common_types.Uri
    "URI to services."

    @classmethod
    def sample(cls):
        return cls(uri='http://example.com/v1/infrastructure',
                   name='infrastructure',
                   type='infrastructure',
                   stacks_uri='http://example.com/v1/infrastructure/stacks',
                   tags=['small'],
                   project_id='1dae5a09ef2b4d8cbf3594b0eb4f6b94',
                   user_id='55f41cf46df74320b9486a35f5d28a11',
                   description='Solum Infrastructure endpoint')


class InfrastructureStack(api_types.Base):
    """Representation of an InfrastructureStack.

    An InfrastructureStack is a set of servers used by Solum for
    infrastructure purpose. It can be a build farm, a set of git servers, bug
    trackers, or more.
    """

    image_id = wtypes.text
    "Unique Identifier of the image"

    heat_stack_id = wtypes.text
    "Unique Identifier of the heat stack associated with this infra stack"

    @classmethod
    def sample(cls):
        return cls(uri='http://example.com/v1/infrastructure/stacks/1234',
                   name='jenkins',
                   type='infrastructure_stack',
                   image_id='1234',
                   heat_stack_id='1234',
                   tags=['small'],
                   project_id='1dae5a09ef2b4d8cbf3594b0eb4f6b94',
                   user_id='55f41cf46df74320b9486a35f5d28a11',
                   description='A jenkins build farm of servers')
