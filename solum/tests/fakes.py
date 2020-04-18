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

import datetime
from unittest import mock

from oslo_utils import uuidutils


fakeAuthTokenHeaders = {'X-User-Id': u'773a902f022949619b5c2f32cd89d419',
                        'X-Roles': u'admin, ResellerAdmin, _member_',
                        'X-Project-Id': u'fake_project_id',
                        'X-Project-Name': 'fake_project_name',
                        'X-User-Name': 'test',
                        'X-Auth-Token': u'5588aebbcdc24e17a061595f80574376',
                        'X-Forwarded-For': u'10.10.10.10, 11.11.11.11',
                        'X-Service-Catalog': u'{test: 12345}',
                        'X-Auth-Url': 'fake_auth_url',
                        'X-Identity-Status': 'Confirmed',
                        'X-Domain-Name': 'domain',
                        'X-Project-Domain-Id': 'project_domain_id',
                        'X-User-Domain-Id': 'user_domain_id',
                        }


class FakePecanRequest(mock.Mock):

    def __init__(self, **kwargs):
        super(FakePecanRequest, self).__init__(**kwargs)
        self.host_url = 'http://test_url:8080/test'
        self.application_url = 'http://test_url:8080/test/'
        self.context = {}
        self.body = ''
        self.content_type = 'text/unicode'
        self.accept = None
        self.params = {}
        self.path = '/v1/services'
        self.headers = fakeAuthTokenHeaders
        self.environ = {}
        self.pecan = dict(content_type=None)
        self.query_string = ''

    def __setitem__(self, index, value):
        setattr(self, index, value)


class FakePecanResponse(mock.Mock):

    def __init__(self, **kwargs):
        super(FakePecanResponse, self).__init__(**kwargs)
        self.status = None
        self.status_code = 200


class FakeApp(mock.Mock):
    def __init__(self, **kwargs):
        super(FakeApp, self).__init__(**kwargs)
        self.__tablename__ = 'app'
        self.__resource__ = 'apps'
        self.user_id = 'fake user id'
        self.project_id = 'fake_project_id'
        self.id = 'test_uuid'
        self.name = 'fakeapp'
        self.description = 'fake app used for testing'
        self.language_pack = 'test_lp'
        self.deleted = False
        self.source = {
            'repository': 'http://github.com/example/a.git',
            'revision': 'master',
            'repo_token': 'test-repo-token',
            'private': False,
            'private_ssh_key': 'test-private-ssh-key'
        }
        self.ports = [80]
        self.workflow_config = {
            'run_cmd': 'python ./main.py',
            'test_cmd': 'python ./tests.py',
        }
        self.stack_id = ''
        self.trigger_actions = ["unittest", "build", "deploy"]
        self.scale_config = dict()
        self.raw_content = "{\"repo_token\": \"test-repo-token\"}"

    def as_dict(self):
        return {
            'user_id': self.user_id,
            'project_id': self.project_id,
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'language_pack': self.language_pack,
            'deleted': self.deleted,
            'source': self.source,
            'ports': self.ports,
            'workflow_config': self.workflow_config,
            'stack_id': self.stack_id,
            'raw_content': self.raw_content
        }


class FakeService(mock.Mock):
    def __init__(self, **kwargs):
        super(FakeService, self).__init__(**kwargs)
        self.__tablename__ = 'service'
        self.__resource__ = 'services'
        self.user_id = 'fake user id'
        self.project_id = 'fake_project_id'
        self.uuid = 'test_uuid'
        self.id = 8
        self.name = 'james'
        self.service_type = 'not_this'
        self.description = 'amazing'
        self.tags = ['this', 'and that']
        self.read_only = True

    def as_dict(self):
        return dict(service_type=self.service_type,
                    user_id=self.user_id,
                    project_id=self.project_id,
                    uuid=self.uuid,
                    id=self.id,
                    name=self.name,
                    tags=self.tags,
                    read_only=self.read_only,
                    description=self.description)


class FakeAuthProtocol(mock.Mock):

    def __init__(self, **kwargs):
        super(FakeAuthProtocol, self).__init__(**kwargs)
        self.app = FakeApp()
        self.config = ''


class FakeSensor(mock.Mock):
    def __init__(self, **kwargs):
        super(FakeSensor, self).__init__(**kwargs)
        self.__tablename__ = 'sensor'
        self.__resource__ = 'sensors'
        self.user_id = 'test_user_id'
        self.project_id = 'fake_project_id'
        self.uuid = '54d54'
        self.id = 'test_id'
        self.name = 'test_name'
        self.value = '42'
        self.sensor_type = 'int'
        self.documentation = 'http://test_documentation.com/'
        self.description = 'test_description'
        self.target_resource = 'http://test_target_resource.com/'

    def as_dict(self):
        return dict(name=self.name,
                    user_id=self.user_id,
                    project_id=self.project_id,
                    uuid=self.uuid,
                    id=self.id,
                    value=self.value,
                    sensor_type=self.sensor_type,
                    documentation=self.documentation,
                    description=self.description,
                    target_resource=self.target_resource)


class FakeExtension(mock.Mock):
    def __init__(self, **kwargs):
        super(FakeExtension, self).__init__(**kwargs)
        self.__tablename__ = 'extension'
        self.__resource__ = 'extension'
        self.user_id = 'user_id'
        self.project_id = 'fake_project_id'
        self.uuid = '44du3dx'
        self.documentation = 'http://test_documentation.com'
        self.description = 'test_desc'
        self.id = 'test_id'
        self.name = 'test_name'
        self.version = '12.3'

    def as_dict(self):
        return dict(name=self.name,
                    user_id=self.user_id,
                    project_id=self.project_id,
                    uuid=self.uuid,
                    id=self.id,
                    version=self.version,
                    documentation=self.documentation,
                    description=self.description)


class FakeExecution(mock.Mock):
    def __init__(self, **kwargs):
        super(FakeExecution, self).__init__(**kwargs)
        self.__tablename__ = 'execution'
        self.__resource__ = 'execution'
        self.uuid = '44du3dx'
        self.id = 'test_id'
        self.pipeline_id = 'pipeline-1-2-3-4'

    def as_dict(self):
        return dict(pipeline_id=self.pipeline_id,
                    uuid=self.uuid,
                    id=self.id)


class FakeInfrastructureStack(mock.Mock):
    def __init__(self, **kwargs):
        super(FakeInfrastructureStack, self).__init__(**kwargs)
        self.__tablename__ = 'build_farm'
        self.__resource__ = 'build_farms'
        self.user_id = 'user_id'
        self.project_id = 'fake_project_id'
        self.uuid = 'ceda0408-c93d-4772-abb2-18f65189d440'
        self.description = 'test_desc'
        self.id = 'test_id'
        self.name = 'test_name'
        self.image_id = '1234'
        self.heat_stack_id = '5678'

    def as_dict(self):
        return dict(name=self.name,
                    user_id=self.user_id,
                    project_id=self.project_id,
                    uuid=self.uuid,
                    id=self.id,
                    image_id=self.image_id,
                    heat_stack_id=self.heat_stack_id,
                    description=self.description)


class FakeWorkflow(mock.Mock):
    def __init__(self, **kwargs):
        super(FakeWorkflow, self).__init__(**kwargs)
        self.__tablename__ = 'workflow'
        self.__resource__ = 'workflows'
        self.id = ''
        self.deleted = False
        self.project_id = 'fake_project_id'
        self.user_id = 'fake_user_id'
        self.app_id = 'fake_app_id'
        self.wf_id = '1'
        self.source = 'fake_source'
        self.config = 'fake_config'
        self.actions = 'fake_actions'
        self.assembly = 1
        self.status = 'BUILT'

    def as_dict(self):
        return dict(user_id=self.user_id,
                    project_id=self.project_id,
                    app_id=self.app_id,
                    source=self.source,
                    config=self.config,
                    actions=self.actions,
                    status=self.status)


class FakeAssembly(mock.Mock):
    def __init__(self, **kwargs):
        super(FakeAssembly, self).__init__(**kwargs)
        self.__tablename__ = 'assembly'
        self.__resource__ = 'assemblies'
        self.user_id = 'fake user id'
        self.project_id = 'fake_project_id'
        self.plan_uuid = 'fake plan uuid'
        self.uuid = 'test_uuid'
        self.id = 8
        self.name = 'faker'
        self.components = [FakeComponent()]
        self.status = 'BUILDING'
        self.application_uri = 'test_uri'
        now = datetime.datetime.utcnow()
        self.created_at = now
        self.updated_at = now
        self.workflow = ['unittest', 'build', 'deploy']
        self.image_id = 8

    def as_dict(self):
        return dict(user_id=self.user_id,
                    project_id=self.project_id,
                    application_uri=self.application_uri,
                    uuid=self.uuid,
                    id=self.id,
                    name=self.name,
                    created_at=self.created_at,
                    updated_at=self.updated_at,
                    status=self.status,
                    workflow=self.workflow)


class FakePipeline(mock.Mock):
    def __init__(self, **kwargs):
        super(FakePipeline, self).__init__(**kwargs)
        self.__tablename__ = 'pipeline'
        self.__resource__ = 'pipelines'
        self.user_id = 'fake user id'
        self.project_id = 'fake_project_id'
        self.plan_uuid = 'fake plan uuid'
        self.uuid = 'test_uuid'
        self.id = 8
        self.name = 'faker'
        self.trust_id = 'trust_worthy'

    def last_execution(self):
        return FakeExecution()

    def as_dict(self):
        return dict(user_id=self.user_id,
                    project_id=self.project_id,
                    uuid=self.uuid,
                    id=self.id,
                    name=self.name)


class FakePlan(mock.Mock):
    def __init__(self, **kwargs):
        super(FakePlan, self).__init__(**kwargs)
        self.__tablename__ = 'plan'
        self.__resource__ = 'plans'
        self.raw_content = ({'name': 'faker',
                            'artifacts': [{'language_pack': 'test_lp'}]})
        self.user_id = 'fake user id'
        self.project_id = 'fake_project_id'
        self.uuid = 'test_uuid'
        self.id = 8
        self.name = 'faker'
        self.deploy_keys_uri = None
        self.trust_id = 'trust_worthy'

    def as_dict(self):
        return dict(raw_content=self.raw_content,
                    user_id=self.user_id,
                    project_id=self.project_id,
                    uuid=self.uuid,
                    id=self.id,
                    name=self.name)

    def refined_content(self):
        if self.raw_content and self.uuid:
            self.raw_content['uuid'] = self.uuid
        return self.raw_content


class FakeImage(mock.Mock):
    def __init__(self, **kwargs):
        super(FakeImage, self).__init__(**kwargs)
        self.__tablename__ = 'image'
        self.__resource__ = 'images'
        self.user_id = 'fake user id'
        self.project_id = 'fake_project_id'
        self.uuid = 'test_uuid'
        self.id = 8
        self.name = 'faker'
        self.source_uri = 'git://here'
        self.description = 'test_desc'
        self.base_image_id = '1-2-3-4'
        self.created_image_id = '7-2-3-4'
        self.image_format = 'docker'
        self.source_format = 'dib'
        self.artifact_type = None
        self.status = 'READY'
        self.external_ref = 'TempUrl'
        self.docker_image_name = 'tenant-name-ts-commit'

    def as_dict(self):
        return dict(user_id=self.user_id,
                    project_id=self.project_id,
                    base_image_id=self.base_image_id,
                    image_format=self.image_format,
                    created_image_id=self.created_image_id,
                    uuid=self.uuid,
                    id=self.id,
                    name=self.name,
                    source_uri=self.source_uri,
                    source_format=self.source_format,
                    description=self.description)


class FakeComponent(mock.Mock):
    def __init__(self, **kwargs):
        super(FakeComponent, self).__init__(**kwargs)
        self.id = 1
        self.__tablename__ = 'component'
        self.__resource__ = 'components'
        self.name = 'james'
        self.service_type = 'not_this'
        self.description = 'amazing'
        self.assembly_id = '1'
        self.parent_component_id = '2'
        self.tags = ['this', 'and that']

    def as_dict(self):
        return dict(service_type=self.service_type,
                    id=self.id,
                    name=self.name,
                    tags=self.tags,
                    assembly_id=self.assembly_id,
                    parent_component_id=self.parent_component_id,
                    description=self.description)


class FakeOperation(mock.Mock):

    def __init__(self, **kwargs):
        super(FakeOperation, self).__init__(**kwargs)
        self.__tablename__ = 'operation'
        self.__resource__ = 'operations'
        self.user_id = 'fake_user_id'
        self.project_id = 'fake_project_id'
        self.uuid = 'fake_uuid'
        self.id = 8
        self.name = 'fake_name'
        self.description = 'fake_description'
        self.tags = ['this', 'and that']
        self.documentation = 'fake_documentation'
        self.target_resource = 'fake_target_resource'

    def as_dict(self):
        return dict(user_id=self.user_id,
                    project_id=self.project_id,
                    uuid=self.uuid,
                    id=self.id,
                    name=self.name,
                    tags=self.tags,
                    documentation=self.documentation,
                    target_resource=self.target_resource,
                    description=self.description)


class FakeAttributeDefinition(mock.Mock):

    def __init__(self, **kwargs):
        super(FakeAttributeDefinition, self).__init__(**kwargs)
        self.name = 'fake_attribute'
        self.type = 'attribute_definition'


class FakeUserlog(mock.Mock):
    def __init__(self, **kwargs):
        super(FakeUserlog, self).__init__(**kwargs)
        self.resource_uuid = uuidutils.generate_uuid()
        self.resource_type = 'app'
        self.location = 'fake location'
        self.strategy = 'local'
        self.strategy_info = '{}'


class FakeParameter(mock.Mock):
    def __init__(self, **kwargs):
        super(FakeParameter, self).__init__(**kwargs)
        self.plan_id = 11
        self.user_defined_params = {'key': 'ab"cd'}
        self.sys_defined_params = {}
