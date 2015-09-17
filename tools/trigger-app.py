#!/usr/bin/env python
# Copyright 2014 - Rackspace Hosting
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

"""
For testing trigger workflow
"""

import argparse
import json
import os

import requests
from solumclient import client as solum_client


SOLUM_API_VERSION = '1'


def _get_solum_client():
    args = {}
    args['os_username'] = os.getenv('OS_USERNAME', '')
    args['os_password'] = os.getenv('OS_PASSWORD', '')
    args['os_tenant_name'] = os.getenv('OS_TENANT_NAME', '')
    args['os_auth_url'] = os.getenv('OS_AUTH_URL', '')
    args['solum_url'] = os.getenv('SOLUM_URL', '')

    try:
        client = solum_client.get_client(SOLUM_API_VERSION, **args)
        return client
    except Exception as ex:
        print("Error in getting Solum client: %s" % ex)
        exit(1)


def main(args):
    client = _get_solum_client()
    app = client.apps.find(name_or_id=args.app)
    status_url = 'https://api.github.com/repos/{repo}/statuses/{sha}'.format(
        repo=args.repo, sha=args.sha)
    body_dict = {'sender': {'url': 'https://api.github.com'},
                 'pull_request': {'head': {'sha': args.sha}},
                 'repository': {'statuses_url': status_url}}
    body = json.dumps(body_dict)
    trigger_uri = app.trigger_uri
    if args.workflow:
        trigger_uri = "%s?workflow=%s" % (trigger_uri, args.workflow)
    resp = requests.post(trigger_uri, data=body)
    print('status code is %s' % resp.status_code)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('app', help="app name/UUID")
    parser.add_argument('--sha', default='xyz', dest='sha',
                        help="the commit sha to clone from")
    parser.add_argument('--repo', default='u/r', dest='repo',
                        help="{user}/{repo}")
    parser.add_argument('--workflow', dest="workflow",
                        help="Workflow to trigger")

    args = parser.parse_args()
    main(args)
