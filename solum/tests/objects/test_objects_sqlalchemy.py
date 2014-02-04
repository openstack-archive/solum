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


class TestObjectsSqlalchemy(tests.BaseTestCase):
    def setUp(self):
        super(tests.BaseTestCase, self).setUp()
        utils.setup_dummy_db()
        utils.reset_dummy_db()
        self.ctx = utils.dummy_context()

    def test_objects_registered(self):
        self.assertIsNotNone(objects.registry.Application)
        self.assertIsNotNone(objects.registry.ApplicationList)

    def test_objects_reloadable(self):
        self.assertIsNotNone(objects.registry.Application)

        objects.registry.clear()

        with testtools.ExpectedException(KeyError):
            objects.registry.Application

        objects.load()

        self.assertIsNotNone(objects.registry.Application)

    def test_object_creatable(self):
        app = objects.registry.Application()
        self.assertIsNotNone(app)
        self.assertIsNone(app.id)

    # (claytonc) Depends on https://bugs.launchpad.net/oslo/+bug/1256954
    # for python 3.3
    # def test_object_duplicate_create(self):
    #     app = objects.registry.Application()
    #     app.create(self.ctx)
    #     app2 = objects.registry.Application()
    #     app2.id = app.id
    #     with testtools.ExpectedException(db_exc.DBError):
    #         app2.create(self.ctx)

    def test_object_raises_not_found(self):
        with testtools.ExpectedException(exception.ApplicationNotFound):
            objects.registry.Application.get_by_id(None, 10000)

    def test_object_persist_and_retrieve(self):
        app = objects.registry.Application()
        self.assertIsNotNone(app)
        app.create(self.ctx)
        self.assertIsNotNone(app.id)

        app2 = objects.registry.Application.get_by_id(None, app.id)
        self.assertIsNotNone(app2)
        self.assertEqual(app.id, app2.id)

        # visible via direct query
        query = utils.get_dummy_session().query(app.__class__)\
            .filter_by(id=app.id)
        app3 = query.first()
        self.assertIsNotNone(app3)
        self.assertEqual(app3.id, app.id)

        # visible via get_all
        apps = objects.registry.ApplicationList.get_all(None)
        exists = [item for item in apps if item.id == app.id]
        self.assertTrue(len(exists) > 0)

    def test_object_mutate(self):
        begin = datetime.datetime.utcnow()

        app = objects.registry.Application()
        self.assertIsNotNone(app)
        app.create(self.ctx)

        self.assertIsNotNone(app.id)
        self.assertThat(app.created_at, matchers.GreaterThan(begin))
        self.assertIsNone(app.updated_at)

        next_time = datetime.datetime.utcnow()

        app.save(self.ctx)

        self.assertThat(next_time, matchers.GreaterThan(app.created_at))
