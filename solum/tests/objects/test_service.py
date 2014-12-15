# Copyright 2014 - Rackspace US, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from solum.objects import registry
from solum.objects.sqlalchemy import service
from solum.tests import base
from solum.tests import utils


class TestService(base.BaseTestCase):
    def setUp(self):
        super(TestService, self).setUp()
        self.db = self.useFixture(utils.Database())
        self.ctx = utils.dummy_context()
        self.data = [{'project_id': 'fake_project_id',
                      'user_id': 'fred',
                      'uuid': '12345678abcdefgh',
                      'name': 'service1',
                      'description': 'test service',
                      'service_type': 'language_pack'}]
        utils.create_models_from_data(service.Service, self.data, self.ctx)

    def test_objects_registered(self):
        self.assertTrue(registry.Service)
        self.assertTrue(registry.ServiceList)

    def test_get_all(self):
        lst = service.ServiceList()
        self.assertEqual(1, len(lst.get_all(self.ctx)))

    def test_check_data(self):
        test_srvc = service.Service().get_by_id(self.ctx, self.data[0]['id'])
        for key, value in self.data[0].items():
            self.assertEqual(value, getattr(test_srvc, key))
