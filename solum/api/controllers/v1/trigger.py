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
from urllib import parse

from oslo_config import cfg
from oslo_log import log as logging
import pecan
from pecan import rest

from solum.api.handlers import app_handler
from solum.common import exception
from solum.common import policy

LOG = logging.getLogger(__name__)
CONF = cfg.CONF


def query_dict(querystring):
    if not querystring:
        return {}
    query = parse.unquote(querystring).rstrip()
    query = query.split('&')
    query = [q.split('=') for q in query]
    return dict([(q[0], ' '.join(q[1:])) for q in query])


class TriggerController(rest.RestController):
    """Manages triggers."""

    def _process_request(self, body):
        commit_sha = ''
        collab_url = None

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
        return commit_sha, collab_url

    def _get_workflow(self, query):
        workflow = None

        if 'workflow' in query:
            valid_stages = ['unittest', 'build', 'deploy']
            workflow = query['workflow'].replace('+', ' ').split(' ')
            workflow = filter(lambda x: x in valid_stages, workflow)
            if not workflow:
                workflow = None
        return workflow

    @exception.wrap_pecan_controller_exception
    @pecan.expose()
    def post(self, trigger_id):
        """Trigger a new event on Solum."""
        policy.check('create_trigger',
                     pecan.request.security_context)
        commit_sha = ''
        status_url = None
        collab_url = None

        try:
            query = query_dict(pecan.request.query_string)
            workflow = self._get_workflow(query)

            body = json.loads(pecan.request.body)
            if ('sender' in body and 'url' in body['sender'] and
                    'api.github.com' in body['sender']['url']):
                action = body.get('action', None)
                if 'comment' in body:
                    # Process a request for rebuilding
                    commit_sha, collab_url = self._process_request(body)
                elif 'pull_request' in body:
                    # Process a GitHub pull request
                    commit_sha = body['pull_request']['head']['sha']
                else:
                    raise exception.NotImplemented()

                # An example of Github statuses_url
                # https://api.github.com/repos/:user/:repo/statuses/{sha}
                if commit_sha:
                    status_url = body['repository']['statuses_url'].format(
                        sha=commit_sha)
            else:
                # Request NOT from a Github repo
                raise exception.NotImplemented()
        except Exception as exc:
            if isinstance(exc, exception.SolumException):
                raise
            info_msg = "Expected fields not found in request body."
            LOG.info(info_msg)
            raise exception.BadRequest(reason=info_msg)

        try:
            # Trigger workflow only on PR create and on rebuild request
            if action in ['created', 'opened', 'edited', 'reopened',
                          'synchronize', 'closed']:
                handler = app_handler.AppHandler(None)
                handler.trigger_workflow(trigger_id, commit_sha, status_url,
                                         collab_url, workflow=workflow)
        except exception.ResourceNotFound:
            LOG.error("Incorrect trigger url.")
            raise

        pecan.response.status = 202
