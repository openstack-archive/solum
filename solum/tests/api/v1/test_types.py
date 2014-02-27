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


from solum.api.controllers.v1.datamodel import plan as plan_api
from solum.objects.sqlalchemy import plan as plan_model
from solum.tests import base
from solum.tests import utils

from solum import objects


class TestTypes(base.BaseTestCase):
    def setUp(self):
        super(TestTypes, self).setUp()
        self.useFixture(utils.Database())

    def test_as_dict(self):
        data = {'name': 'test_hb',
                'uri': 'http://test_host/v1/plans/hb',
                'project_id': 'a3266ef8-b3fa-4ab8-b468-d42b5fab5c4d',
                'user_id': '59a9da1f-9a19-4f1e-8877-120865da716b'}
        p = plan_api.Plan(**data)
        del data['uri']
        self.assertEqual(data, p.as_dict(plan_model.Plan))

    def test_as_dict_from_keys(self):
        data = {'name': 'test_hb',
                'project_id': 'a3266ef8-b3fa-4ab8-b468-d42b5fab5c4d'}
        p = plan_api.Plan(**data)
        self.assertEqual(data, p.as_dict_from_keys(['name', 'project_id']))

    def test_from_db_model(self):
        obj = objects.registry.Plan()
        data = {'uuid': '8705981d-162b-4431-943e-53609fdc1750',
                'name': 'test_hb',
                'project_id': '3594fb87-487f-44f8-889a-c76bec06174c',
                'user_id': 'd724ff2b-0035-457d-9afc-07f6efa3f0a5',
                'does_not_exist': 'n/a'}
        obj.update(data)
        host_url = 'http://test_host'
        p = plan_api.Plan.from_db_model(obj, host_url)
        self.assertEqual(data['name'], p.name)
        self.assertEqual(data['project_id'], p.project_id)
        self.assertEqual('plan', p.type)
        self.assertEqual(data['user_id'], p.user_id)
        self.assertEqual('%s/v1/%s/%s' % (host_url, obj.__resource__,
                                          data['uuid']), p.uri)
