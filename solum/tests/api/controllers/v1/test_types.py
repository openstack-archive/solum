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

from wsme import types as wtypes

from solum.api.controllers.v1.datamodel import component as component_api
from solum.api.controllers.v1.datamodel import types as api_types
from solum import objects
from solum.objects.sqlalchemy import component as component_model
from solum.tests import base
from solum.tests import utils


class TestTypes(base.BaseTestCase):
    def setUp(self):
        super(TestTypes, self).setUp()
        self.useFixture(utils.Database())

    def test_as_dict(self):
        data = {'name': 'test_hb',
                'uri': 'http://test_host/v1/components/hb',
                'project_id': 'a3266ef8-b3fa-4ab8-b468-d42b5fab5c4d',
                'user_id': '59a9da1f-9a19-4f1e-8877-120865da716b'}
        a = component_api.Component(**data)
        del data['uri']
        self.assertEqual(data, a.as_dict(component_model.Component))

    def test_as_dict_from_keys(self):
        data = {'name': 'test_hb',
                'project_id': 'a3266ef8-b3fa-4ab8-b468-d42b5fab5c4d'}
        a = component_api.Component(**data)
        self.assertEqual(data, a.as_dict_from_keys(['name', 'project_id']))

    def test_from_db_model(self):
        obj = objects.registry.Component()
        data = {'uuid': '8705981d-162b-4431-943e-53609fdc1750',
                'name': 'test_hb',
                'project_id': '3594fb87-487f-44f8-889a-c76bec06174c',
                'user_id': 'd724ff2b-0035-457d-9afc-07f6efa3f0a5',
                'does_not_exist': 'n/a'}
        obj.update(data)
        host_url = 'http://test_host'
        c = component_api.Component.from_db_model(obj, host_url)
        self.assertEqual(data['name'], c.name)
        self.assertEqual(data['project_id'], c.project_id)
        self.assertEqual('component', c.type)
        self.assertEqual(data['user_id'], c.user_id)
        self.assertEqual('%s/v1/%s/%s' % (host_url, obj.__resource__, None),
                         c.uri)
        self.assertIsNone(c.assembly_uuid)

    def test_from_db_model_extra_keys(self):
        assembly_data = {'uuid': '42d',
                         'name': 'test_assembly',
                         'plan_id': 1,
                         'project_id': '3594fb87-487f-44f8-889a-c76bec06174c',
                         'user_id': 'd724ff2b-0035-457d-9afc-07f6efa3f0a5'}
        a = objects.registry.Assembly(**assembly_data)
        a.create(utils.dummy_context())
        data = {'uuid': '8705981d-162b-4431-943e-53609fdc1750',
                'name': 'test_hb',
                'project_id': '3594fb87-487f-44f8-889a-c76bec06174c',
                'user_id': 'd724ff2b-0035-457d-9afc-07f6efa3f0a5',
                'assembly_uuid': assembly_data['uuid']}
        obj = objects.registry.Component(**data)
        c = component_api.Component.from_db_model(obj, 'http://test_host')
        self.assertEqual(assembly_data['uuid'], c.assembly_uuid)


class TestMultiType(base.BaseTestCase):

    def test_valid_values(self):
        vt = api_types.MultiType(wtypes.text, bool)
        value = vt.validate("somestring")
        self.assertEqual("somestring", value)
        value = vt.validate(True)
        self.assertTrue(value)

    def test_invalid_values(self):
        vt = api_types.MultiType(wtypes.text, bool)
        self.assertRaises(ValueError, vt.validate, 10)
        self.assertRaises(ValueError, vt.validate, 0.10)
        self.assertRaises(ValueError, vt.validate, object())

    def test_multitype_tostring(self):
        vt = api_types.MultiType(wtypes.text, bool)
        vts = str(vt)
        self.assertIn(str(wtypes.text), vts)
        self.assertIn(str(bool), vts)
        self.assertNotIn(str(int), vts)


class TestTypeNames(base.BaseTestCase):

    scenarios = [
        ('punct', dict(
            in_value='.,', expect_ok=False)),
        ('-', dict(
            in_value='a-b', expect_ok=True)),
        ('_', dict(
            in_value='a_b', expect_ok=True)),
        ('spaces', dict(
            in_value='look a space', expect_ok=False)),
        ('special', dict(
            in_value='$-&', expect_ok=False)),
        ('upper', dict(
            in_value='ALLGOOD', expect_ok=True)),
        ('lower', dict(
            in_value='evenbetter', expect_ok=True)),
        ('numbers', dict(
            in_value='12345', expect_ok=True)),
    ]

    def test_name(self):
        if self.expect_ok:
            s = component_api.Component(name=self.in_value)
            self.assertEqual(self.in_value, s.name)
        else:
            self.assertRaises(ValueError, component_api.Component,
                              name=self.in_value)
