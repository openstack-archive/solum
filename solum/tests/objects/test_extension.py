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
from solum.objects.sqlalchemy import extension
from solum.tests import base
from solum.tests import utils


class TestExtension(base.BaseTestCase):
    def setUp(self):
        super(TestExtension, self).setUp()
        self.db = self.useFixture(utils.Database())
        self.ctx = utils.dummy_context()

        self.data = [{'uuid': 'test-uuid-42',
                      'project_id': self.ctx.project_id,
                      'user_id': '55f41cf46df74320b9486a35f5d28a11',
                      'name': 'logstash',
                      'version': '2.13',
                      'description': 'This logstash extension provides a tool'
                                     ' for managing your application events'
                                     ' and logs.',
                      'documentation': 'http://example.com/docs/ext/logstash',
                      }]
        utils.create_models_from_data(extension.Extension, self.data, self.ctx)

    def test_objects_registered(self):
        self.assertTrue(registry.Extension)
        self.assertTrue(registry.ExtensionList)

    def test_get_all(self):
        lst = extension.ExtensionList()
        self.assertIsNotNone(lst)
        self.assertEqual(1, len(lst.get_all(self.ctx)))

    def test_check_data_by_id(self):
        e = extension.Extension().get_by_id(self.ctx, self.data[0]['id'])
        self.assertIsNotNone(e)
        for key, value in self.data[0].items():
            self.assertEqual(value, getattr(e, key))

    def test_check_data_by_uuid(self):
        e = extension.Extension().get_by_uuid(self.ctx, self.data[0]['uuid'])
        self.assertIsNotNone(e)
        for key, value in self.data[0].items():
            self.assertEqual(value, getattr(e, key))
