# Copyright 2014 - Rackspace
#
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

import sqlalchemy as sa

from solum.objects.sqlalchemy import models as sql
from solum.objects import userlog as abstract


class Userlog(sql.Base, abstract.Userlog):
    """Represent a userlog in sqlalchemy."""

    __tablename__ = 'userlogs'
    __resource__ = 'userlogs'
    __table_args__ = sql.table_args()

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    assembly_uuid = sa.Column(sa.String(36), nullable=False)
    created_at = sa.Column(sa.DateTime)
    location = sa.Column(sa.String(255))
    strategy = sa.Column(sa.String(255))
    strategy_info = sa.Column(sa.String(1024))


class UserlogList(abstract.UserlogList):
    """Represent a list of userlogs in sqlalchemy."""

    @classmethod
    def get_all(cls, context):
        return UserlogList(sql.model_query(context, Userlog))
