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

import json
from unittest import mock

from oslo_config import cfg

from solum.api.controllers.v1 import trigger
from solum.tests import base
from solum.tests import fakes


@mock.patch('pecan.request', new_callable=fakes.FakePecanRequest)
@mock.patch('pecan.response', new_callable=fakes.FakePecanResponse)
@mock.patch('solum.api.controllers.v1.trigger.app_handler'
            '.AppHandler')
class TestTriggerController(base.BaseTestCase):

    def test_trigger_get_workflow_with_empty_body(self, assem_mock,
                                                  resp_mock, request_mock):
        obj = trigger.TriggerController()
        workflow = obj._get_workflow({})
        self.assertIsNone(workflow)

    def test_trigger_get_workflow_with_deploy(self, assem_mock,
                                              resp_mock, request_mock):
        obj = trigger.TriggerController()
        query = {'workflow': 'deploy'}
        workflow = obj._get_workflow(query)
        self.assertEqual(['deploy'], list(workflow))

    def test_trigger_get_workflow_with_build_deploy(self, assem_mock,
                                                    resp_mock, request_mock):
        obj = trigger.TriggerController()
        query = {'workflow': 'build+deploy'}
        workflow = obj._get_workflow(query)
        self.assertEqual(['build', 'deploy'], list(workflow))

    def test_trigger_get_workflow_with_all(self, assem_mock,
                                           resp_mock, request_mock):
        obj = trigger.TriggerController()
        query = {'workflow': 'unittest+build+deploy'}
        workflow = obj._get_workflow(query)
        self.assertEqual(['unittest', 'build', 'deploy'], list(workflow))

    def test_trigger_get_workflow_with_invalid_stage(self, assem_mock,
                                                     resp_mock, request_mock):
        obj = trigger.TriggerController()
        query = {'workflow': 'unittest+unitunitunittest'}
        workflow = obj._get_workflow(query)
        self.assertEqual(['unittest'], list(workflow))

    def test_trigger_process_request_private_repo(self, assem_mock,
                                                  resp_mock, request_mock):
        cfg.CONF.api.rebuild_phrase = "solum retry tests"
        status_url = 'https://api.github.com/repos/u/r/statuses/{sha}'
        collab_url = ('https://api.github.com/repos/u/r/' +
                      'collaborators{/collaborator}')
        body_dict = {'sender': {'url': 'https://api.github.com'},
                     'comment': {'commit_id': 'asdf',
                                 'body': '  SOLUM retry tests ',
                                 'user': {'login': 'u'}},
                     'repository': {'statuses_url': status_url,
                                    'collaborators_url': collab_url,
                                    'private': True}}
        obj = trigger.TriggerController()
        commit_sha, collab_url = obj._process_request(body_dict)
        self.assertIsNone(collab_url)
        self.assertEqual('asdf', commit_sha)

    def test_trigger_process_request_on_valid_pub_repo(self,
                                                       assem_mock, resp_mock,
                                                       request_mock):
        cfg.CONF.api.rebuild_phrase = "solum retry tests"
        status_url = 'https://api.github.com/repos/u/r/statuses/{sha}'
        collab_url = ('https://api.github.com/repos/u/r/' +
                      'collaborators{/collaborator}')
        body_dict = {'sender': {'url': 'https://api.github.com'},
                     'comment': {'commit_id': 'asdf',
                                 'body': 'solum retry tests',
                                 'user': {'login': 'u'}},
                     'repository': {'statuses_url': status_url,
                                    'collaborators_url': collab_url,
                                    'private': False}}
        obj = trigger.TriggerController()
        commit_sha, collab_url = obj._process_request(body_dict)
        self.assertEqual('https://api.github.com/repos/u/r/collaborators/u',
                         collab_url)
        self.assertEqual('asdf', commit_sha)

    @mock.patch('solum.common.policy.check')
    def test_trigger_post_with_empty_body(self, mock_policy, assem_mock,
                                          resp_mock, request_mock):
        mock_policy.return_value = True
        obj = trigger.TriggerController()
        obj.post('test_id')
        self.assertEqual(400, resp_mock.status)
        tw = assem_mock.return_value.trigger_workflow
        assert not tw.called

    @mock.patch('solum.common.policy.check')
    def test_trigger_post_on_github_webhook(self, mock_policy, assem_mock,
                                            resp_mock, request_mock):
        mock_policy.return_value = True
        status_url = 'https://api.github.com/repos/u/r/statuses/{sha}'
        body_dict = {'sender': {'url': 'https://api.github.com'},
                     'action': 'opened',
                     'pull_request': {'head': {'sha': 'asdf'}},
                     'repository': {'statuses_url': status_url}}
        expected_st_url = 'https://api.github.com/repos/u/r/statuses/asdf'
        request_mock.body = json.dumps(body_dict)
        obj = trigger.TriggerController()
        obj.post('test_id')
        self.assertEqual(202, resp_mock.status)
        tw = assem_mock.return_value.trigger_workflow
        tw.assert_called_once_with('test_id', 'asdf', expected_st_url, None,
                                   workflow=None)

    @mock.patch('solum.common.policy.check')
    def test_trigger_post_on_github_comment_webhook(self, mock_policy,
                                                    assem_mock, resp_mock,
                                                    request_mock):
        mock_policy.return_value = True
        cfg.CONF.api.rebuild_phrase = "solum retry tests"
        status_url = 'https://api.github.com/repos/u/r/statuses/{sha}'
        collab_url = ('https://api.github.com/repos/u/r/' +
                      'collaborators{/collaborator}')
        body_dict = {'sender': {'url': 'https://api.github.com'},
                     'action': 'created',
                     'comment': {'commit_id': 'asdf',
                                 'body': '  SOLUM retry tests ',
                                 'user': {'login': 'u'}},
                     'repository': {'statuses_url': status_url,
                                    'collaborators_url': collab_url,
                                    'private': True}}
        expected_st_url = 'https://api.github.com/repos/u/r/statuses/asdf'
        request_mock.body = json.dumps(body_dict)
        obj = trigger.TriggerController()
        obj.post('test_id')
        self.assertEqual(202, resp_mock.status)
        tw = assem_mock.return_value.trigger_workflow
        tw.assert_called_once_with('test_id', 'asdf', expected_st_url, None,
                                   workflow=None)

    @mock.patch('httplib2.Http.request')
    @mock.patch('solum.common.policy.check')
    def test_trigger_post_on_mismatch_comment_pub_repo(self, http_mock,
                                                       mock_policy,
                                                       assem_mock, resp_mock,
                                                       request_mock):
        mock_policy.return_value = True
        cfg.CONF.api.rebuild_phrase = "solum retry tests"
        status_url = 'https://api.github.com/repos/u/r/statuses/{sha}'
        collab_url = ('https://api.github.com/repos/u/r/' +
                      'collaborators{/collaborator}')
        body_dict = {'sender': {'url': 'https://api.github.com'},
                     'action': 'created',
                     'comment': {'commit_id': 'asdf',
                                 'body': 'solum is awesome',
                                 'user': {'login': 'u'}},
                     'repository': {'statuses_url': status_url,
                                    'collaborators_url': collab_url,
                                    'private': False}}
        request_mock.body = json.dumps(body_dict)
        http_mock.return_value = ({'status': '204'}, '')  # a collaborator
        obj = trigger.TriggerController()
        obj.post('test_id')
        self.assertEqual(403, resp_mock.status)
        tw = assem_mock.return_value.trigger_workflow
        assert not tw.called

    @mock.patch('httplib2.Http.request')
    @mock.patch('solum.common.policy.check')
    def test_trigger_post_on_valid_comment_pub_repo(self, http_mock,
                                                    mock_policy,
                                                    assem_mock, resp_mock,
                                                    request_mock):
        mock_policy.return_value = True
        cfg.CONF.api.rebuild_phrase = "solum retry tests"
        status_url = 'https://api.github.com/repos/u/r/statuses/{sha}'
        collab_url = ('https://api.github.com/repos/u/r/' +
                      'collaborators{/collaborator}')
        body_dict = {'sender': {'url': 'https://api.github.com'},
                     'action': 'created',
                     'comment': {'commit_id': 'asdf',
                                 'body': 'solum retry tests',
                                 'user': {'login': 'u'}},
                     'repository': {'statuses_url': status_url,
                                    'collaborators_url': collab_url,
                                    'private': False}}
        expected_st_url = 'https://api.github.com/repos/u/r/statuses/asdf'
        expected_clb_url = 'https://api.github.com/repos/u/r/collaborators/u'
        request_mock.body = json.dumps(body_dict)
        http_mock.return_value = ({'status': '204'}, '')  # Valid collaborator
        obj = trigger.TriggerController()
        obj.post('test_id')
        self.assertEqual(202, resp_mock.status)
        tw = assem_mock.return_value.trigger_workflow
        tw.assert_called_once_with('test_id', 'asdf', expected_st_url,
                                   expected_clb_url, workflow=None)

    @mock.patch('solum.common.policy.check')
    def test_trigger_post_on_comment_missing_login(self, mock_policy,
                                                   assem_mock, resp_mock,
                                                   request_mock):
        mock_policy.return_value = True
        cfg.CONF.api.rebuild_phrase = "solum retry tests"
        status_url = 'https://api.github.com/repos/u/r/statuses/{sha}'
        collab_url = ('https://api.github.com/repos/u/r/' +
                      'collaborators{/collaborator}')
        body_dict = {'sender': {'url': 'https://api.github.com'},
                     'comment': {'commit_id': 'asdf',
                                 'body': 'solum retry tests',
                                 'user': 'MISSING_LOGIN'},
                     'repository': {'statuses_url': status_url,
                                    'collaborators_url': collab_url,
                                    'private': False}}
        request_mock.body = json.dumps(body_dict)
        obj = trigger.TriggerController()
        obj.post('test_id')
        self.assertEqual(400, resp_mock.status)
        tw = assem_mock.return_value.trigger_workflow
        assert not tw.called

    @mock.patch('solum.common.policy.check')
    def test_trigger_post_on_wrong_github_webhook(self, mock_policy,
                                                  assem_mock,
                                                  resp_mock, request_mock):
        mock_policy.return_value = True
        status_url = 'https://api.github.com/repos/u/r/statuses/{sha}'
        body_dict = {'sender': {'url': 'https://api.github.com'},
                     'pull_request': {'head': {'sha': 'asdf'}},
                     'repository': {'HACKED_statuses_url': status_url}}
        request_mock.body = json.dumps(body_dict)
        obj = trigger.TriggerController()
        obj.post('test_id')
        self.assertEqual(400, resp_mock.status)
        tw = assem_mock.return_value.trigger_workflow
        assert not tw.called

    @mock.patch('solum.common.policy.check')
    def test_trigger_post_on_unknown_git_webhook(self, mock_policy, assem_mock,
                                                 resp_mock, request_mock):
        mock_policy.return_value = True
        body_dict = {"pull_request": {"head": {"sha": "asdf"}}}
        request_mock.body = json.dumps(body_dict)
        obj = trigger.TriggerController()
        obj.post('test_id')
        self.assertEqual(501, resp_mock.status)
        tw = assem_mock.return_value.trigger_workflow
        assert not tw.called

    @mock.patch('solum.common.policy.check')
    def test_trigger_post_on_non_github_webhook(self, mock_policy, assem_mock,
                                                resp_mock, request_mock):
        mock_policy.return_value = True
        body_dict = {"sender": {"url": "https://non-github.com"},
                     "pull_request": {"head": {"sha": "asdf"}}}
        request_mock.body = json.dumps(body_dict)
        obj = trigger.TriggerController()
        obj.post('test_id')
        self.assertEqual(501, resp_mock.status)
        tw = assem_mock.return_value.trigger_workflow
        assert not tw.called

    @mock.patch('solum.common.policy.check')
    def test_trigger_post_on_github_ping_webhook(self, mock_policy, assem_mock,
                                                 resp_mock, request_mock):
        mock_policy.return_value = True
        body_dict = {"sender": {"url": "https://api.github.com"},
                     "zen": "Keep it logically awesome."}
        request_mock.body = json.dumps(body_dict)
        obj = trigger.TriggerController()
        obj.post('test_id')
        self.assertEqual(501, resp_mock.status)
        tw = assem_mock.return_value.trigger_workflow
        assert not tw.called
