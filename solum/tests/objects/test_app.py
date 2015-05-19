# Copyright 2015 - Rackspace US, Inc.
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
from solum.objects.sqlalchemy import app
from solum.tests import base
from solum.tests import utils


class TestApp(base.BaseTestCase):
    def setUp(self):
        super(TestApp, self).setUp()
        self.db = self.useFixture(utils.Database())
        self.ctx = utils.dummy_context()
        self.data = [{'id': 'test-uuid-555',
                      'project_id': self.ctx.tenant,
                      'user_id': 'fred',
                      'name': 'testapp',
                      'description': 'fake app for testing',
                      }]
        utils.create_models_from_data(app.App, self.data, self.ctx)

    def test_objects_registered(self):
        self.assertTrue(registry.App)
        self.assertTrue(registry.AppList)

    def test_get_all(self):
        lst = app.AppList()
        self.assertEqual(1, len(lst.get_all(self.ctx)))

    def test_check_data_by_id(self):
        foundapp = app.App().get_by_id(self.ctx, self.data[0]['id'])
        for key, value in self.data[0].items():
            self.assertEqual(value, getattr(foundapp, key))

    def test_check_data_by_uuid(self):
        foundapp = app.App().get_by_uuid(self.ctx, self.data[0]['id'])
        for key, value in self.data[0].items():
            self.assertEqual(value, getattr(foundapp, key))
