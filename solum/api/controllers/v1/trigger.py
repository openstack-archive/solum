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

from oslo.config import cfg
import pecan
from pecan import rest

from solum.api.handlers import assembly_handler
from solum.api.handlers import pipeline_handler
from solum.common import exception
from solum.openstack.common import log as logging

LOG = logging.getLogger(__name__)
CONF = cfg.CONF


class TriggerController(rest.RestController):
    """Manages triggers."""

    @exception.wrap_pecan_controller_exception
    @pecan.expose()
    def post(self, trigger_id):
        """Trigger a new event on Solum."""
        commit_sha = ''
        status_url = None
        collab_url = None
        try:
            body = json.loads(pecan.request.body)
            if ('sender' in body and 'url' in body['sender'] and
                    'api.github.com' in body['sender']['url']):
                if 'comment' in body:
                    # Process a request for rebuilding
                    phrase = body['comment']['body']
                    commenter = body['comment']['user']['login']
                    private_repo = body['repository']['private']
                    # An example of collab_url
                    # https://api.github.com/repos/:user/:repo/collaborators{/collaborator}
                    if not private_repo:
                        # Only verify collaborator for public repos
                        collab_url = (
                            body['repository']['collaborators_url'].format(
                                **{'/collaborator': '/' + commenter}))
                    if (phrase.strip('. ').lower() !=
                            CONF.api.rebuild_phrase.lower()):
                        err_msg = 'Rebuild phrase does not match'
                        raise exception.RequestForbidden(reason=err_msg)
                    else:
                        commit_sha = body['comment']['commit_id']
                elif 'pull_request' in body:
                    # Process a GitHub pull request
                    commit_sha = body['pull_request']['head']['sha']

                # An exmaple of Github statuses_url
                # https://api.github.com/repos/:user/:repo/statuses/{sha}
                if commit_sha:
                    status_url = body['repository']['statuses_url'].format(
                        sha=commit_sha)
        except StandardError:
            LOG.info("Expected fields not found in request body.")

        try:
            handler = assembly_handler.AssemblyHandler(None)
            handler.trigger_workflow(trigger_id, commit_sha, status_url,
                                     collab_url)
        except exception.ResourceNotFound:
            handler = pipeline_handler.PipelineHandler(None)
            handler.trigger_workflow(trigger_id)

        pecan.response.status = 202
