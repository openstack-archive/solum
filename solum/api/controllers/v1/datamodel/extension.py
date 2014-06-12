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


class Extension(api_types.Base):
    """The Extension resource represents Provider modifications.

    This may include additional protocol semantics, resource types,
    application lifecycle states, resource attributes, etc. Anything may be
    added, as long as it does not contradict the base functionality offered
    by Solum.
    """

    version = wtypes.text
    "Version of the extension."

    documentation = common_types.Uri
    "Documentation URI to the extension."

    @classmethod
    def sample(cls):
        return cls(uri='http://example.com/v1/extensions/logstash',
                   name='logstash',
                   type='extension',
                   tags=['large'],
                   project_id='1dae5a09ef2b4d8cbf3594b0eb4f6b94',
                   user_id='55f41cf46df74320b9486a35f5d28a11',
                   description='This logstash extension provides a tool for '
                               'managing your application events and logs.',
                   version='2.13',
                   documentation='http://example.com/docs/ext/logstash')
