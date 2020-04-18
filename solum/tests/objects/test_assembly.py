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

from sqlalchemy.orm import exc as sqla_ex
from unittest import mock

from solum.common import exception
from solum.objects import registry
from solum.objects.sqlalchemy import assembly
from solum.tests import base
from solum.tests import utils

from oslo_utils import uuidutils


class TestAssembly(base.BaseTestCase):
    def setUp(self):
        super(TestAssembly, self).setUp()
        self.db = self.useFixture(utils.Database())
        self.ctx = utils.dummy_context()

        self.data = [{'project_id': self.ctx.tenant,
                      'uuid': 'ce43e347f0b0422825245b3e5f140a81cef6e65b',
                      'user_id': 'fred',
                      'name': 'assembly1',
                      'description': 'test assembly',
                      'tags': 'assembly tags',
                      'plan_id': 'plan_id_1',
                      'status': 'BUILDING',
                      'application_uri': 'http://192.168.78.21:5000'}]
        utils.create_models_from_data(assembly.Assembly, self.data, self.ctx)

    def test_objects_registered(self):
        self.assertTrue(registry.Assembly)
        self.assertTrue(registry.AssemblyList)

    def test_get_all(self):
        lst = assembly.AssemblyList()
        self.assertEqual(1, len(lst.get_all(self.ctx)))

    def test_check_data(self):
        ta = assembly.Assembly().get_by_id(self.ctx, self.data[0]['id'])
        for key, value in self.data[0].items():
            self.assertEqual(value, getattr(ta, key))

    def test_del_assem_with_comps(self):
        ta = registry.Assembly().get_by_id(self.ctx, self.data[0]['id'])
        comp = registry.Component()
        comp.uuid = uuidutils.generate_uuid()
        comp.name = 't'
        comp.assembly_id = ta.id
        comp.create(self.ctx)
        comp_id = comp.id
        ta.destroy(self.ctx)

        self.assertRaises(exception.ResourceNotFound,
                          registry.Assembly().get_by_id,
                          self.ctx, self.data[0]['id'])
        self.assertRaises(exception.ResourceNotFound,
                          registry.Component().get_by_id, self.ctx, comp_id)

    def test_update_and_save(self):
        # first update
        assembly.Assembly().update_and_save(self.ctx, self.data[0]['id'],
                                            {'status': 'DELETING'})
        updated = assembly.Assembly().get_by_id(self.ctx, self.data[0]['id'])
        self.assertEqual('DELETING', getattr(updated, 'status'))

        # second update, 'DELETING' status is not updatable
        assembly.Assembly().update_and_save(self.ctx, self.data[0]['id'],
                                            {'status': 'DEPLOYMENT_COMPLETE'})
        updated = assembly.Assembly().get_by_id(self.ctx, self.data[0]['id'])
        self.assertEqual('DELETING', getattr(updated, 'status'))

    @mock.patch('solum.objects.sqlalchemy.models.SolumBase.get_session')
    @mock.patch('solum.objects.sqlalchemy.models.LOG')
    def test_update_and_save_raise_exp(self, mock_log, mock_sess):
        mock_sess.return_value.merge.side_effect = sqla_ex.StaleDataError
        self.assertRaises(sqla_ex.StaleDataError,
                          assembly.Assembly().update_and_save,
                          self.ctx, self.data[0]['id'], {'status': 'DELETING'})
        expected = [mock.call("Failed DB call update_and_save. "
                              "Retrying 2 more times."),
                    mock.call("Failed DB call update_and_save. "
                              "Retrying 1 more times."),
                    mock.call("Failed DB call update_and_save. "
                              "Retrying 0 more times.")]
        self.assertEqual(expected, mock_log.warning.call_args_list)
