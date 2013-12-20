# Copyright 2013 - Red Hat, Inc.
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


class Base(wtypes.Base):
    """Base class for all API types."""

    uri = common_types.Uri
    "URI to the resource."

    name = wtypes.text
    "Name of the resource."

    type = wtypes.text
    "The resource type."

    description = wtypes.text
    "Textual description of the resource."

    tags = [wtypes.text]
    "Tags for the resource."

    project_id = wtypes.text
    "The project that this resource belongs in."

    user_id = wtypes.text
    "The user that owns this resource."
