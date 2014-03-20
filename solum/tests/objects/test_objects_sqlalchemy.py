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
import uuid

import testtools
from testtools import matchers

from solum.common import exception
from solum import objects
from solum.tests import base as tests
from solum.tests import utils


class TestObjectsSqlalchemy(tests.BaseTestCase):
    def setUp(self):
        super(tests.BaseTestCase, self).setUp()
        self.ctx = utils.dummy_context()
        self.useFixture(utils.Database())

    def test_objects_reloadable(self):
        self.assertIsNotNone(objects.registry.Plan)

        objects.registry.clear()

        with testtools.ExpectedException(KeyError):
            objects.registry.Plan

        objects.load()

        self.assertIsNotNone(objects.registry.Plan)

    def test_object_creatable(self):
        plan = objects.registry.Plan()
        self.assertIsNotNone(plan)
        self.assertIsNone(plan.id)

    # (claytonc) Depends on https://bugs.launchpad.net/oslo/+bug/1256954
    # for python 3.3
    # def test_object_duplicate_create(self):
    #     plan = objects.registry.Plan()
    #     plan.create(self.ctx)
    #     plan2 = objects.registry.Plan()
    #     plan2.id = plan.id
    #     with testtools.ExpectedException(db_exc.DBError):
    #         plan2.create(self.ctx)

    def test_object_raises_not_found(self):
        with testtools.ExpectedException(exception.ResourceNotFound):
            objects.registry.Plan.get_by_id(None, 10000)

    def test_object_persist_and_retrieve(self):
        plan = objects.registry.Plan()
        self.assertIsNotNone(plan)
        plan.uuid = str(uuid.uuid4())
        plan.name = 'abc'
        plan.description = '1-2-3-4'
        plan.create(self.ctx)
        self.assertIsNotNone(plan.id)

        plan2 = objects.registry.Plan.get_by_id(None, plan.id)
        self.assertIsNotNone(plan2)
        self.assertEqual(plan.id, plan2.id)
        self.assertEqual(plan.uuid, plan2.uuid)
        self.assertEqual(plan.name, plan2.name)
        self.assertEqual(plan.description, plan2.description)

        # visible via direct query
        query = utils.get_dummy_session().query(plan.__class__)\
            .filter_by(id=plan.id)
        plan3 = query.first()
        self.assertIsNotNone(plan3)
        self.assertEqual(plan3.id, plan.id)

        # visible via get_all
        plans = objects.registry.PlanList.get_all(None)
        exists = [item for item in plans if item.id == plan.id]
        self.assertTrue(len(exists) > 0)

    def test_object_mutate(self):
        begin = datetime.datetime.utcnow()

        plan = objects.registry.Plan()
        self.assertIsNotNone(plan)
        plan.uuid = str(uuid.uuid4())
        plan.create(self.ctx)

        self.assertIsNotNone(plan.id)
        self.assertThat(plan.created_at, matchers.GreaterThan(begin))
        self.assertIsNone(plan.updated_at)

        next_time = datetime.datetime.utcnow()

        plan.save(self.ctx)

        self.assertThat(next_time, matchers.GreaterThan(plan.created_at))
