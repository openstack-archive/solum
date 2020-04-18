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


from solum.api.controllers.v1.datamodel import pipeline as pipelinemodel
from solum.api.controllers.v1 import pipeline
from solum.common import exception
from solum import objects
from solum.tests import base
from solum.tests import fakes


@mock.patch('solum.common.policy.check')
@mock.patch('pecan.request', new_callable=fakes.FakePecanRequest)
@mock.patch('pecan.response', new_callable=fakes.FakePecanResponse)
@mock.patch('solum.api.handlers.pipeline_handler.PipelineHandler')
class TestPipelineController(base.BaseTestCase):
    def setUp(self):
        super(TestPipelineController, self).setUp()
        objects.load()

    def test_pipeline_get(self, PipelineHandler, resp_mock,
                          request_mock, mock_policy):
        mock_policy.return_value = True
        hand_get = PipelineHandler.return_value.get
        fake_pipeline = fakes.FakePipeline()
        hand_get.return_value = fake_pipeline
        resp = pipeline.PipelineController('test_id').get()
        self.assertIsNotNone(fake_pipeline)
        self.assertEqual(fake_pipeline.name, resp['result'].name)
        self.assertEqual(fake_pipeline.project_id, resp['result'].project_id)
        self.assertEqual(fake_pipeline.uuid, resp['result'].uuid)
        self.assertEqual(fake_pipeline.user_id, resp['result'].user_id)
        hand_get.assert_called_with('test_id')
        self.assertEqual(200, resp_mock.status)

    def test_pipeline_get_not_found(self, PipelineHandler,
                                    resp_mock, request_mock, mock_policy):
        mock_policy.return_value = True
        hand_get = PipelineHandler.return_value.get
        hand_get.side_effect = exception.ResourceNotFound(
            name='pipeline', pipeline_id='test_id')
        pipeline.PipelineController('test_id').get()
        hand_get.assert_called_with('test_id')
        self.assertEqual(404, resp_mock.status)

    def test_pipeline_put_none(self, PipelineHandler, resp_mock,
                               request_mock, mock_policy):
        mock_policy.return_value = True
        request_mock.body = None
        request_mock.content_type = 'application/json'
        hand_put = PipelineHandler.return_value.put
        hand_put.return_value = fakes.FakePipeline()
        pipeline.PipelineController('test_id').put()
        self.assertEqual(400, resp_mock.status)

    def test_pipeline_put_not_found(self, PipelineHandler,
                                    resp_mock, request_mock, mock_policy):
        mock_policy.return_value = True
        json_update = {'name': 'foo'}
        request_mock.body = json.dumps(json_update)
        request_mock.content_type = 'application/json'
        hand_update = PipelineHandler.return_value.update
        hand_update.side_effect = exception.ResourceNotFound(
            name='pipeline', pipeline_id='test_id')
        pipeline.PipelineController('test_id').put()
        hand_update.assert_called_with('test_id', json_update)
        self.assertEqual(404, resp_mock.status)

    def test_pipeline_put_ok(self, PipelineHandler, resp_mock,
                             request_mock, mock_policy):
        mock_policy.return_value = True
        json_update = {'name': 'foo'}
        request_mock.body = json.dumps(json_update)
        request_mock.content_type = 'application/json'
        hand_update = PipelineHandler.return_value.update
        hand_update.return_value = fakes.FakePipeline()
        pipeline.PipelineController('test_id').put()
        hand_update.assert_called_with('test_id', json_update)
        self.assertEqual(200, resp_mock.status)

    def test_pipeline_delete_not_found(self, PipelineHandler,
                                       resp_mock, request_mock, mock_policy):
        mock_policy.return_value = True
        hand_delete = PipelineHandler.return_value.delete
        hand_delete.side_effect = exception.ResourceNotFound(
            name='pipeline', pipeline_id='test_id')
        pipeline.PipelineController('test_id').delete()
        hand_delete.assert_called_with('test_id')
        self.assertEqual(404, resp_mock.status)

    def test_pipeline_delete_ok(self, PipelineHandler,
                                resp_mock, request_mock, mock_policy):
        mock_policy.return_value = True
        hand_delete = PipelineHandler.return_value.delete
        hand_delete.return_value = None
        pipeline.PipelineController('test_id').delete()
        hand_delete.assert_called_with('test_id')
        self.assertEqual(204, resp_mock.status)


class TestPipelineAsDict(base.BaseTestCase):

    scenarios = [
        ('none', dict(data=None)),
        ('one', dict(data={'name': 'foo'})),
        ('full', dict(data={'uri': 'http://example.com/v1/pipelines/x1',
                            'name': 'Example-pipeline',
                            'type': 'pipeline',
                            'project_id': '1dae5a09ef2b4d8cbf3594b0eb4f6b94',
                            'user_id': '55f41cf46df74320b9486a35f5d28a11'}))
    ]

    def test_as_dict(self):
        objects.load()
        if self.data is None:
            s = pipelinemodel.Pipeline()
            self.data = {}
        else:
            s = pipelinemodel.Pipeline(**self.data)
        if 'uri' in self.data:
            del self.data['uri']
        if 'type' in self.data:
            del self.data['type']

        self.assertEqual(self.data, s.as_dict(objects.registry.Pipeline))


@mock.patch('solum.common.policy.check')
@mock.patch('pecan.request', new_callable=fakes.FakePecanRequest)
@mock.patch('pecan.response', new_callable=fakes.FakePecanResponse)
@mock.patch('solum.api.handlers.pipeline_handler.PipelineHandler')
class TestPipelinesController(base.BaseTestCase):
    def setUp(self):
        super(TestPipelinesController, self).setUp()
        objects.load()

    def test_pipelines_get_all(self, PipelineHandler,
                               resp_mock, request_mock, mock_policy):
        mock_policy.return_value = True
        hand_get = PipelineHandler.return_value.get_all
        fake_pipeline = fakes.FakePipeline()
        hand_get.return_value = [fake_pipeline]
        resp = pipeline.PipelinesController().get_all()
        self.assertEqual(fake_pipeline.name, resp['result'][0].name)
        self.assertEqual(fake_pipeline.project_id,
                         resp['result'][0].project_id)
        self.assertEqual(fake_pipeline.uuid, resp['result'][0].uuid)
        self.assertEqual(fake_pipeline.user_id, resp['result'][0].user_id)
        hand_get.assert_called_with()
        self.assertEqual(200, resp_mock.status)
        self.assertIsNotNone(resp)

    @mock.patch('solum.objects.registry.Plan')
    def test_pipelines_post(self, mock_Plan, PipelineHandler,
                            resp_mock, request_mock, mock_policy):
        mock_policy.return_value = True
        json_create = {'name': 'foo',
                       'plan_uri': 'http://test_url:8080/test/911'}
        request_mock.body = json.dumps(json_create)
        request_mock.content_type = 'application/json'
        request_mock.security_context = None
        mock_Plan.get_by_uuid.return_value = fakes.FakePlan()

        hand_create = PipelineHandler.return_value.create
        hand_create.return_value = fakes.FakePipeline()
        pipeline.PipelinesController().post()
        hand_create.assert_called_with({'name': 'foo',
                                        'plan_id': 8})
        mock_Plan.get_by_uuid.assert_called_with(None, '911')
        self.assertEqual(201, resp_mock.status)

    def test_pipelines_post_no_plan(self, PipelineHandler, resp_mock,
                                    request_mock, mock_policy):
        mock_policy.return_value = True
        json_create = {'name': 'foo'}
        request_mock.body = json.dumps(json_create)
        request_mock.content_type = 'application/json'
        hand_create = PipelineHandler.return_value.create
        hand_create.return_value = fakes.FakePipeline()
        pipeline.PipelinesController().post()
        ret_val = pipeline.PipelinesController().post()
        faultstring = str(ret_val['faultstring'])
        self.assertIn('The plan was not given or could not be found',
                      faultstring)
        self.assertEqual(400, resp_mock.status)

    def test_pipelines_post_not_hosted(self, PipelineHandler, resp_mock,
                                       request_mock, mock_policy):
        mock_policy.return_value = True
        json_create = {'name': 'foo',
                       'plan_uri': 'http://example.com/a.git'}
        request_mock.body = json.dumps(json_create)
        request_mock.content_type = 'application/json'
        hand_create = PipelineHandler.return_value.create
        hand_create.return_value = fakes.FakePipeline()
        ret_val = pipeline.PipelinesController().post()
        faultstring = str(ret_val['faultstring'])
        self.assertIn('The plan was not hosted in solum', faultstring)
        self.assertEqual(400, resp_mock.status)

    def test_pipelines_post_nodata(self, PipelineHandler,
                                   resp_mock, request_mock, mock_policy):
        mock_policy.return_value = True
        request_mock.body = ''
        request_mock.content_type = 'application/json'
        hand_create = PipelineHandler.return_value.create
        hand_create.return_value = fakes.FakePipeline()
        ret_val = pipeline.PipelinesController().post()
        faultstring = str(ret_val['faultstring'])
        self.assertEqual("Missing argument: \"data\"", faultstring)
        self.assertEqual(400, resp_mock.status)
