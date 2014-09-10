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


import json

import pecan
from pecan import rest

from solum.api.handlers import assembly_handler
from solum.api.handlers import pipeline_handler
from solum.common import exception
from solum.openstack.common import log as logging

LOG = logging.getLogger(__name__)


class TriggerController(rest.RestController):
    """Manages triggers."""

    @exception.wrap_pecan_controller_exception
    @pecan.expose()
    def post(self, trigger_id):
        """Trigger a new event on Solum."""
        branch_name = 'master'
        status_url = None
        try:
            body = json.loads(pecan.request.body)
            if ('sender' in body and 'url' in body['sender'] and
                    'api.github.com' in body['sender']['url']):
                # Process a GitHub pull request
                branch_name = body['pull_request']['head']['ref']
                # An exmaple of Github statuses_url
                # https://api.github.com/repos/:user/:repo/statuses/{sha}
                status_url = body['pull_request']['statuses_url']
        except StandardError:
            LOG.info("Expected fields not found in request body.")

        try:
            handler = assembly_handler.AssemblyHandler(None)
            handler.trigger_workflow(trigger_id, branch_name, status_url)
        except exception.ResourceNotFound:
            handler = pipeline_handler.PipelineHandler(None)
            handler.trigger_workflow(trigger_id)

        pecan.response.status = 202
