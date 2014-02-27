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

from solum.objects import assembly as abstract
from solum.objects.sqlalchemy import models as sql
from solum.openstack.common.db.sqlalchemy import session as db_session


class Assembly(sql.Base, abstract.Assembly):
    """Represent an assembly in sqlalchemy."""

    __tablename__ = 'assembly'
    __resource__ = 'assemblies'
    __table_args__ = sql.table_args()

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    uuid = sa.Column(sa.String(36), nullable=False)
    project_id = sa.Column(sa.String(36))
    user_id = sa.Column(sa.String(36))
    name = sa.Column(sa.String(100))
    description = sa.Column(sa.String(255))
    tags = sa.Column(sa.Text)
    plan_id = sa.Column(sa.Integer, sa.ForeignKey('plan.id'), nullable=False)

    @classmethod
    def get_by_uuid(cls, context, item_uuid):
        try:
            return db_session.get_session().query(cls).filter_by(
                uuid=item_uuid).one()
        except sa.orm.exc.NoResultFound:
            cls._raise_not_found(item_uuid)


class AssemblyList(abstract.AssemblyList):
    """Represent a list of assemblies in sqlalchemy."""

    @classmethod
    def get_all(cls, context):
        return AssemblyList(sql.model_query(context, Assembly))
