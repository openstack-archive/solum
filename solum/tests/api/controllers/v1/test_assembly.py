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


from solum.api.controllers.v1 import assembly
from solum.api.controllers.v1.datamodel import assembly as assemblymodel
from solum.common import exception
from solum import objects
from solum.tests import base
from solum.tests import fakes


@mock.patch('solum.common.policy.check')
@mock.patch('pecan.request', new_callable=fakes.FakePecanRequest)
@mock.patch('pecan.response', new_callable=fakes.FakePecanResponse)
@mock.patch('solum.api.handlers.assembly_handler.AssemblyHandler')
class TestAssemblyController(base.BaseTestCase):
    def setUp(self):
        super(TestAssemblyController, self).setUp()
        objects.load()

    def test_assembly_get(self, AssemblyHandler, resp_mock,
                          request_mock, mock_policy):
        mock_policy.return_value = True
        hand_get = AssemblyHandler.return_value.get
        fake_assembly = fakes.FakeAssembly()
        hand_get.return_value = fake_assembly
        cont = assembly.AssemblyController('test_id')
        resp = cont.get()
        self.assertIsNotNone(fake_assembly)
        self.assertEqual(fake_assembly.name, resp['result'].name)
        self.assertEqual(fake_assembly.project_id, resp['result'].project_id)
        self.assertEqual(fake_assembly.uuid, resp['result'].uuid)
        self.assertEqual(fake_assembly.status, resp['result'].status)
        self.assertEqual(fake_assembly.user_id, resp['result'].user_id)
        self.assertEqual(fake_assembly.application_uri,
                         resp['result'].application_uri)
        self.assertEqual(fake_assembly.created_at, resp['result'].created_at)
        self.assertEqual(fake_assembly.updated_at, resp['result'].updated_at)
        hand_get.assert_called_with('test_id')
        self.assertEqual(200, resp_mock.status)

    def test_assembly_get_not_found(self, AssemblyHandler,
                                    resp_mock, request_mock, mock_policy):
        mock_policy.return_value = True
        hand_get = AssemblyHandler.return_value.get
        hand_get.side_effect = exception.ResourceNotFound(
            name='assembly', assembly_id='test_id')
        cont = assembly.AssemblyController('test_id')
        cont.get()
        hand_get.assert_called_with('test_id')
        self.assertEqual(404, resp_mock.status)

    def test_assembly_put_none(self, AssemblyHandler, resp_mock,
                               request_mock, mock_policy):
        mock_policy.return_value = True
        request_mock.body = None
        request_mock.content_type = 'application/json'
        hand_put = AssemblyHandler.return_value.put
        hand_put.return_value = fakes.FakeAssembly()
        assembly.AssemblyController('test_id').put()
        self.assertEqual(400, resp_mock.status)

    def test_assembly_put_not_found(self, AssemblyHandler,
                                    resp_mock, request_mock, mock_policy):
        mock_policy.return_value = True
        json_update = {'name': 'foo'}
        request_mock.body = json.dumps(json_update)
        request_mock.content_type = 'application/json'
        hand_update = AssemblyHandler.return_value.update
        hand_update.side_effect = exception.ResourceNotFound(
            name='assembly', assembly_id='test_id')
        assembly.AssemblyController('test_id').put()
        hand_update.assert_called_with('test_id', json_update)
        self.assertEqual(404, resp_mock.status)

    def test_assembly_put_ok(self, AssemblyHandler, resp_mock,
                             request_mock, mock_policy):
        mock_policy.return_value = True
        json_update = {'name': 'foo'}
        request_mock.body = json.dumps(json_update)
        request_mock.content_type = 'application/json'
        hand_update = AssemblyHandler.return_value.update
        hand_update.return_value = fakes.FakeAssembly()
        assembly.AssemblyController('test_id').put()
        hand_update.assert_called_with('test_id', json_update)
        self.assertEqual(200, resp_mock.status)

    def test_assembly_delete_not_found(self, AssemblyHandler,
                                       resp_mock, request_mock, mock_policy):
        mock_policy.return_value = True
        hand_delete = AssemblyHandler.return_value.delete
        hand_delete.side_effect = exception.ResourceNotFound(
            name='assembly', assembly_id='test_id')
        obj = assembly.AssemblyController('test_id')
        obj.delete()
        hand_delete.assert_called_with('test_id')
        self.assertEqual(404, resp_mock.status)

    def test_assembly_delete_ok(self, AssemblyHandler,
                                resp_mock, request_mock, mock_policy):
        mock_policy.return_value = True
        hand_delete = AssemblyHandler.return_value.delete
        hand_delete.return_value = None
        obj = assembly.AssemblyController('test_id')
        obj.delete()
        hand_delete.assert_called_with('test_id')
        self.assertEqual(204, resp_mock.status)


class TestAssemblyAsDict(base.BaseTestCase):

    scenarios = [
        ('none', dict(data=None)),
        ('one', dict(data={'name': 'foo'})),
        ('full', dict(data={'uri': 'http://example.com/v1/assemblies/x1',
                            'name': 'Example-assembly',
                            'type': 'assembly',
                            'project_id': '1dae5a09ef2b4d8cbf3594b0eb4f6b94',
                            'user_id': '55f41cf46df74320b9486a35f5d28a11'}))
    ]

    def test_as_dict(self):
        objects.load()
        if self.data is None:
            s = assemblymodel.Assembly()
            self.data = {}
        else:
            s = assemblymodel.Assembly(**self.data)
        if 'uri' in self.data:
            del self.data['uri']
        if 'type' in self.data:
            del self.data['type']

        self.assertEqual(self.data, s.as_dict(objects.registry.Assembly))


@mock.patch('solum.common.policy.check')
@mock.patch('pecan.request', new_callable=fakes.FakePecanRequest)
@mock.patch('pecan.response', new_callable=fakes.FakePecanResponse)
@mock.patch('solum.api.handlers.assembly_handler.AssemblyHandler')
class TestAssembliesController(base.BaseTestCase):
    def setUp(self):
        super(TestAssembliesController, self).setUp()
        objects.load()

    def test_assemblies_get_all(self, AssemblyHandler,
                                resp_mock, request_mock, mock_policy):
        mock_policy.return_value = True
        hand_get = AssemblyHandler.return_value.get_all
        fake_assembly = fakes.FakeAssembly()
        hand_get.return_value = [fake_assembly]
        resp = assembly.AssembliesController().get_all()
        self.assertEqual(fake_assembly.name, resp['result'][0].name)
        self.assertEqual(fake_assembly.project_id,
                         resp['result'][0].project_id)
        self.assertEqual(fake_assembly.uuid, resp['result'][0].uuid)
        self.assertEqual(fake_assembly.status, resp['result'][0].status)
        self.assertEqual(fake_assembly.user_id, resp['result'][0].user_id)
        self.assertEqual(fake_assembly.application_uri,
                         resp['result'][0].application_uri)
        hand_get.assert_called_with()
        self.assertEqual(200, resp_mock.status)
        self.assertIsNotNone(resp)

    @mock.patch('solum.objects.registry.Plan')
    def test_assemblies_post(self, mock_Plan, AssemblyHandler,
                             resp_mock, request_mock, mock_policy):
        mock_policy.return_value = True
        json_create = {'name': 'foo',
                       'plan_uri': 'http://test_url:8080/test/911'}
        request_mock.body = json.dumps(json_create)
        request_mock.content_type = 'application/json'
        request_mock.security_context = None
        mock_Plan.get_by_uuid.return_value = fakes.FakePlan()

        hand_create = AssemblyHandler.return_value.create
        hand_create.return_value = fakes.FakeAssembly()
        assembly.AssembliesController().post()
        hand_create.assert_called_with({'name': 'foo',
                                        'plan_id': 8})
        mock_Plan.get_by_uuid.assert_called_with(None, '911')
        self.assertEqual(201, resp_mock.status)

    def test_assemblies_post_no_plan(self, AssemblyHandler, resp_mock,
                                     request_mock, mock_policy):
        mock_policy.return_value = True
        json_create = {'name': 'foo'}
        request_mock.body = json.dumps(json_create)
        request_mock.content_type = 'application/json'
        hand_create = AssemblyHandler.return_value.create
        hand_create.return_value = fakes.FakeAssembly()
        assembly.AssembliesController().post()
        ret_val = assembly.AssembliesController().post()
        faultstring = str(ret_val['faultstring'])
        self.assertIn('The plan was not given or could not be found',
                      faultstring)
        self.assertEqual(400, resp_mock.status)

    def test_assemblies_post_not_hosted(self, AssemblyHandler, resp_mock,
                                        request_mock, mock_policy):
        mock_policy.return_value = True
        json_create = {'name': 'foo',
                       'plan_uri': 'http://example.com/a.git'}
        request_mock.body = json.dumps(json_create)
        request_mock.content_type = 'application/json'
        hand_create = AssemblyHandler.return_value.create
        hand_create.return_value = fakes.FakeAssembly()
        ret_val = assembly.AssembliesController().post()
        faultstring = str(ret_val['faultstring'])
        self.assertIn('The plan was not hosted in solum', faultstring)
        self.assertEqual(400, resp_mock.status)

    def test_assem_post_nodata(self, AssemblyHandler, resp_mock,
                               request_mock, mock_policy):
        mock_policy.return_value = True
        request_mock.body = ''
        request_mock.content_type = 'application/json'
        hand_create = AssemblyHandler.return_value.create
        hand_create.return_value = fakes.FakeAssembly()
        ret_val = assembly.AssembliesController().post()
        faultstring = str(ret_val['faultstring'])
        self.assertEqual("Missing argument: \"data\"", faultstring)
        self.assertEqual(400, resp_mock.status)
