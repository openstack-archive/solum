# -*- coding: utf-8 -*-
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

import mock


class FakePecanRequest(mock.Mock):

    def __init__(self, **kwargs):
        super(FakePecanRequest, self).__init__(**kwargs)
        self.host_url = 'http://test_url:8080/test'
        self.context = {}
        self.body = ''
        self.content_type = 'text/unicode'
        self.params = {}

    def __setitem__(self, index, value):
        setattr(self, index, value)


class FakePecanResponse(mock.Mock):

    def __init__(self, **kwargs):
        super(FakePecanResponse, self).__init__(**kwargs)
        self.status = None


class FakeApp:
    pass


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
        self.project_id = 'test_project_id'
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
