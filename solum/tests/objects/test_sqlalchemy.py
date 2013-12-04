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
test_sqlalchemy
----------------------------------

Tests for the sqlalchemy implementation helpers
"""

from solum.objects.sqlalchemy import models
from solum.tests import base as tests
from solum.tests import utils


class TestSqlalchemyModels(tests.BaseTestCase):
    def test_sqlalchemy_mysql_table_params(self):
        with utils.patch_connection_url('mysql://'):
            self.assertEqual('InnoDB', models.table_args()['mysql_engine'])
        with utils.patch_connection_url('MySQL://'):
            self.assertEqual('InnoDB', models.table_args()['mysql_engine'])

        with utils.patch_connection_url('sqlite://'):
            self.assertIsNone(models.table_args())
