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

import os.path
import tempfile

import fixtures
from oslo.config import cfg

from solum import objects
from solum.openstack.common.db.sqlalchemy.migration_cli \
    import manager as migration_manager
from solum.openstack.common.db.sqlalchemy import session

CONF = cfg.CONF


def dummy_context(user='test_username', tenant_id='test_tenant_id'):
    return {}


class Database(fixtures.Fixture):

    def __init__(self):
        super(Database, self).__init__()
        self.db_file = None
        with tempfile.NamedTemporaryFile(suffix='.sqlite',
                                         delete=False) as test_file:
            # note the temp file gets deleted by the NestedTempfile fixture.
            self.db_file = test_file.name
        self.engine = session.get_engine()
        # make sure the current connection is cleaned up.
        self.engine.dispose()
        session.cleanup()

    def setUp(self):
        super(Database, self).setUp()
        self.configure()
        self.upgrade()
        self.addCleanup(self.engine.dispose)
        self.engine = session.get_engine()
        self.engine.connect()
        objects.load()

    def upgrade(self):
        alembic_path = os.path.join(os.path.dirname(__file__),
                                    '..', 'objects', 'sqlalchemy',
                                    'migration', 'alembic.ini')
        migrate_path = os.path.join(os.path.dirname(__file__),
                                    '..', 'objects', 'sqlalchemy',
                                    'migration', 'alembic_migrations')
        migration_config = {'alembic_ini_path': alembic_path,
                            'migration_repo_path': migrate_path,
                            'alembic_repo_path': migrate_path}

        manager = migration_manager.MigrationManager(migration_config)
        manager.upgrade('head')

    def configure(self):
        session.set_defaults(sql_connection="sqlite:///%s" % self.db_file,
                             sqlite_db=self.db_file)
        cfg.CONF.set_default('sqlite_synchronous', False)


def get_dummy_session():
    return session.get_session()
