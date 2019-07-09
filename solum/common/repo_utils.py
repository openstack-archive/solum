# Copyright 2014 - Rackspace Hosting
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

import json
import requests
import socket

import httplib2
from oslo_config import cfg
from oslo_log import log as logging

from solum.common import exception


LOG = logging.getLogger(__name__)

http_timeout_opt = [
    cfg.IntOpt('http_request_timeout',
               default=2,
               help='Timeout value in seconds for sending http requests')
]


def list_opts():
    yield 'api', http_timeout_opt


CONF = cfg.CONF
CONF.register_opts(http_timeout_opt, group='api')

CONF.import_opt('log_url_prefix', 'solum.worker.config', group='worker')
http_req_timeout = CONF.api.http_request_timeout


def get_http_connection():
    return httplib2.Http(timeout=http_req_timeout)


def is_reachable(url):
    reachable = False
    conn = get_http_connection()
    resp, _ = conn.request(url, 'GET')
    if resp is not None and resp['status'] == '200':
        reachable = True
    return reachable


def send_status(test_result, status_url, repo_token, pending=False):
    if status_url and repo_token:
        commit_id = status_url.rstrip('/').split('/')[-1]
        log_url = cfg.CONF.worker.log_url_prefix + commit_id
        headers = {'Authorization': 'token ' + repo_token,
                   'Content-Type': 'application/json'}
        if pending:
            data = {'state': 'pending',
                    'description': 'Solum says: Testing in progress',
                    'target_url': log_url}
        elif test_result == 0:
            data = {'state': 'success',
                    'description': 'Solum says: Tests passed',
                    'target_url': log_url}
        else:
            data = {'state': 'failure',
                    'description': 'Solum says: Tests failed',
                    'target_url': log_url}

        resp = requests.post(status_url, headers=headers,
                             data=json.dumps(data))
        if resp.status_code != '201':
            LOG.debug("Failed to send back status. Error code %s,"
                      "status_url %s, repo_token %s" %
                      (resp.status_code, status_url, repo_token))
    else:
        LOG.debug("No url or token available to send back status")


def verify_artifact(artifact, collab_url):
    # TODO(james_li): verify if the artifact is the one that gets triggered
    if collab_url is None:
        return True

    repo_token = artifact.get('repo_token')
    if repo_token is None:
        return False

    headers = {'Authorization': 'token ' + repo_token}
    try:
        conn = get_http_connection()
        resp, _ = conn.request(collab_url, headers=headers)
        if resp['status'] == '204':
            return True
        elif resp['status'] == '404':
            raise exception.RequestForbidden(
                reason="User %s not allowed to do rebuild" %
                       collab_url.split('/')[-1])
    except (httplib2.HttpLib2Error, socket.error) as ex:
        LOG.warning("Error in verifying collaborator, collab url: %s,"
                    " error: %s" % (collab_url, ex))
    return False
