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
from pecan import rest

from solum.api.handlers import assembly_handler
from solum.common import exception


class TriggerController(rest.RestController):
    """Manages triggers."""

    @pecan.expose()
    def post(self, trigger_id):
        """Trigger a new event on Solum."""
        handler = assembly_handler.AssemblyHandler(None)
        try:
            handler.trigger_workflow(trigger_id)
        except exception.ResourceNotFound as excp:
            pecan.response.status = excp.code
            pecan.response.text = excp.message
            return
        pecan.response.status = 202
