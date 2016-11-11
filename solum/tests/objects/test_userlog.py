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
from solum.objects.sqlalchemy import userlog
from solum.tests import base
from solum.tests import utils

from oslo_utils import uuidutils


class TestUserlog(base.BaseTestCase):
    def setUp(self):
        super(TestUserlog, self).setUp()
        self.db = self.useFixture(utils.Database())
        self.ctx = utils.dummy_context()
        a_id = uuidutils.generate_uuid()

        self.data = [{'id': 12,
                      'resource_uuid': '%s' % a_id,
                      'resource_type': 'app',
                      'strategy': 'local',
                      'location': '/dev/null',
                      'project_id': self.ctx.tenant,
                      'strategy_info': '{}',
                      }]
        utils.create_models_from_data(userlog.Userlog, self.data, self.ctx)

    def test_objects_registered(self):
        self.assertTrue(registry.Userlog)
        self.assertTrue(registry.UserlogList)

    def test_get_all(self):
        lst = userlog.UserlogList()
        self.assertEqual(1, len(lst.get_all(self.ctx)))

    def test_check_data(self):
        ulog = userlog.Userlog().get_by_id(self.ctx, self.data[0]['id'])
        for key, value in self.data[0].items():
            self.assertEqual(value, getattr(ulog, key))
