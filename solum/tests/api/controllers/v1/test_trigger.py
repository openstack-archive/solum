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

import mock
from oslo.config import cfg

from solum.api.controllers.v1 import trigger
from solum.common import exception
from solum.tests import base
from solum.tests import fakes


@mock.patch('pecan.request', new_callable=fakes.FakePecanRequest)
@mock.patch('pecan.response', new_callable=fakes.FakePecanResponse)
@mock.patch('solum.api.controllers.v1.trigger.assembly_handler'
            '.AssemblyHandler')
@mock.patch('solum.api.controllers.v1.trigger.pipeline_handler'
            '.PipelineHandler')
class TestTriggerController(base.BaseTestCase):
    def test_trigger_post(self, pipe_mock, assem_mock,
                          resp_mock, request_mock):
        obj = trigger.TriggerController()
        obj.post('test_id')
        self.assertEqual(202, resp_mock.status)
        tw = assem_mock.return_value.trigger_workflow
        tw.assert_called_once_with('test_id', '', None, None)

    def test_trigger_post_on_github_webhook(self, pipe_mock, assem_mock,
                                            resp_mock, request_mock):
        status_url = 'https://api.github.com/repos/u/r/statuses/{sha}'
        body_dict = {'sender': {'url': 'https://api.github.com'},
                     'pull_request': {'head': {'sha': 'asdf'}},
                     'repository': {'statuses_url': status_url}}
        expected_st_url = 'https://api.github.com/repos/u/r/statuses/asdf'
        request_mock.body = json.dumps(body_dict)
        obj = trigger.TriggerController()
        obj.post('test_id')
        self.assertEqual(202, resp_mock.status)
        tw = assem_mock.return_value.trigger_workflow
        tw.assert_called_once_with('test_id', 'asdf', expected_st_url, None)

    def test_trigger_post_on_github_comment_webhook(self, pipe_mock,
                                                    assem_mock, resp_mock,
                                                    request_mock):
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
        expected_st_url = 'https://api.github.com/repos/u/r/statuses/asdf'
        request_mock.body = json.dumps(body_dict)
        obj = trigger.TriggerController()
        obj.post('test_id')
        self.assertEqual(202, resp_mock.status)
        tw = assem_mock.return_value.trigger_workflow
        tw.assert_called_once_with('test_id', 'asdf', expected_st_url, None)

    @mock.patch('httplib2.Http.request')
    def test_trigger_post_on_mismatch_comment_pub_repo(self, http_mock,
                                                       pipe_mock,
                                                       assem_mock, resp_mock,
                                                       request_mock):
        cfg.CONF.api.rebuild_phrase = "solum retry tests"
        status_url = 'https://api.github.com/repos/u/r/statuses/{sha}'
        collab_url = ('https://api.github.com/repos/u/r/' +
                      'collaborators{/collaborator}')
        body_dict = {'sender': {'url': 'https://api.github.com'},
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
    def test_trigger_post_on_valid_comment_pub_repo(self, http_mock,
                                                    pipe_mock,
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
        expected_st_url = 'https://api.github.com/repos/u/r/statuses/asdf'
        expected_clb_url = 'https://api.github.com/repos/u/r/collaborators/u'
        request_mock.body = json.dumps(body_dict)
        http_mock.return_value = ({'status': '204'}, '')  # Valid collaborator
        obj = trigger.TriggerController()
        obj.post('test_id')
        self.assertEqual(202, resp_mock.status)
        tw = assem_mock.return_value.trigger_workflow
        tw.assert_called_once_with('test_id', 'asdf', expected_st_url,
                                   expected_clb_url)

    def test_trigger_post_on_comment_missing_login(self, pipe_mock,
                                                   assem_mock, resp_mock,
                                                   request_mock):
        cfg.CONF.api.rebuild_phrase = "solum retry tests"
        status_url = 'https://api.github.com/repos/u/r/statuses/{sha}'
        collab_url = ('https://api.github.com/repos/u/r/' +
                      'collaborators{/collaborator}')
        body_dict = {'sender': {'url': 'https://api.github.com'},
                     'comment': {'commit_id': 'asdf',
                                 'body': 'solum retry tests',
                                 'user': 'MISING_LOGIN'},
                     'repository': {'statuses_url': status_url,
                                    'collaborators_url': collab_url,
                                    'private': False}}
        request_mock.body = json.dumps(body_dict)
        obj = trigger.TriggerController()
        obj.post('test_id')
        self.assertEqual(202, resp_mock.status)
        tw = assem_mock.return_value.trigger_workflow
        tw.assert_called_once_with('test_id', '', None, None)

    def test_trigger_post_on_wrong_github_webhook(self, pipe_mock, assem_mock,
                                                  resp_mock, request_mock):
        status_url = 'https://api.github.com/repos/u/r/statuses/{sha}'
        body_dict = {'sender': {'url': 'https://api.github.com'},
                     'pull_request': {'head': {'sha': 'asdf'}},
                     'repository': {'HACKED_statuses_url': status_url}}
        request_mock.body = json.dumps(body_dict)
        obj = trigger.TriggerController()
        obj.post('test_id')
        self.assertEqual(202, resp_mock.status)
        tw = assem_mock.return_value.trigger_workflow
        tw.assert_called_once_with('test_id', 'asdf', None, None)

    def test_trigger_post_on_unknown_git_webhook(self, pipe_mock, assem_mock,
                                                 resp_mock, request_mock):
        request_mock.body = ('"pull_request": {"head": {"sha": "asdf"}}}')
        obj = trigger.TriggerController()
        obj.post('test_id')
        self.assertEqual(202, resp_mock.status)
        tw = assem_mock.return_value.trigger_workflow
        tw.assert_called_once_with('test_id', '', None, None)

    def test_trigger_post_on_non_github_webhook(self, pipe_mock, assem_mock,
                                                resp_mock, request_mock):
        request_mock.body = ('{"sender": {"url" :"https://non-github.com"},' +
                             '"pull_request": {"head": {"sha": "asdf"}}}')
        obj = trigger.TriggerController()
        obj.post('test_id')
        self.assertEqual(202, resp_mock.status)
        tw = assem_mock.return_value.trigger_workflow
        tw.assert_called_once_with('test_id', '', None, None)

    def test_trigger_post_pipeline(self, pipe_mock, assem_mock,
                                   resp_mock, request_mock):
        obj = trigger.TriggerController()
        assem_mock.return_value.trigger_workflow.side_effect = (
            exception.ResourceNotFound(name='trigger', id='test_id'))
        obj.post('test_id')

        self.assertEqual(202, resp_mock.status)
        tw = pipe_mock.return_value.trigger_workflow
        tw.assert_called_once_with('test_id')

    def test_trigger_post_none(self, pipe_mock, assem_mock,
                               resp_mock, request_mock):
        obj = trigger.TriggerController()
        assem_mock.return_value.trigger_workflow.side_effect = (
            exception.ResourceNotFound(name='trigger', id='test_id'))
        pipe_mock.return_value.trigger_workflow.side_effect = (
            exception.ResourceNotFound(name='trigger', id='test_id'))
        obj.post('test_id')
        self.assertEqual(404, resp_mock.status)
        tw = assem_mock.return_value.trigger_workflow
        tw.assert_called_once_with('test_id', '', None, None)
        tw = pipe_mock.return_value.trigger_workflow
        tw.assert_called_once_with('test_id')
