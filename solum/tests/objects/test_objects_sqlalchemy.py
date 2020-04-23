# Copyright 2013 - Red Hat, Inc.
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

"""
test_objects
----------------------------------

Tests for the sqlalchemy solum 'objects' implementation
"""

import datetime

import testtools
from testtools import matchers

from solum.common import exception
from solum import objects
from solum.tests import base as tests
from solum.tests import utils

from oslo_utils import uuidutils


class TestObjectsSqlalchemy(tests.BaseTestCase):
    def setUp(self):
        super(tests.BaseTestCase, self).setUp()
        self.ctx = utils.dummy_context()
        self.useFixture(utils.Database())

    def test_objects_reloadable(self):
        self.assertIsNotNone(objects.registry.Component)

        objects.registry.clear()

        objects.registry.Component

        objects.load()

        self.assertIsNotNone(objects.registry.Component)

    def test_object_creatable(self):
        component = objects.registry.Component()
        self.assertIsNotNone(component)
        self.assertIsNone(component.id)

    # (claytonc) Depends on https://bugs.launchpad.net/oslo/+bug/1256954
    # for python 3.3
    # def test_object_duplicate_create(self):
    #     component = objects.registry.Component()
    #     component.create(self.ctx)
    #     component2 = objects.registry.Component()
    #     component2.id = component.id
    #     with testtools.ExpectedException(db_exc.DBError):
    #         component2.create(self.ctx)

    def test_object_raises_not_found(self):
        with testtools.ExpectedException(exception.ResourceNotFound):
            objects.registry.Component.get_by_id(None, 10000)

    def test_object_persist_and_retrieve(self):
        component = objects.registry.Component()
        self.assertIsNotNone(component)
        component.uuid = uuidutils.generate_uuid()
        component.name = 'abc'
        component.description = '1-2-3-4'
        component.plan_id = 1
        component.create(self.ctx)
        self.assertIsNotNone(component.id)

        component2 = objects.registry.Component.get_by_id(None, component.id)
        self.assertIsNotNone(component2)
        self.assertEqual(component.id, component2.id)
        self.assertEqual(component.uuid, component2.uuid)
        self.assertEqual(component.name, component2.name)
        self.assertEqual(component.description, component2.description)

        # visible via direct query
        dsession = utils.get_dummy_session()
        query = dsession.query(component.__class__).filter_by(id=component.id)
        component3 = query.first()
        self.assertIsNotNone(component3)
        self.assertEqual(component3.id, component3.id)

        # visible via get_all
        components = objects.registry.ComponentList.get_all(None)
        exists = [item for item in components if item.id == component.id]
        self.assertGreater(len(exists), 0)

    def test_object_mutate(self):
        begin = datetime.datetime.utcnow()

        component = objects.registry.Component()
        self.assertIsNotNone(component)
        component.uuid = uuidutils.generate_uuid()
        component.plan_id = 1
        component.create(self.ctx)

        self.assertIsNotNone(component.id)
        self.assertThat(component.created_at, matchers.GreaterThan(begin))
        self.assertIsNone(component.updated_at)

        next_time = datetime.datetime.utcnow()

        component.save(self.ctx)

        self.assertThat(next_time, matchers.GreaterThan(component.created_at))
