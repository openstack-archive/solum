# Copyright 2015 - Rackspace, Inc.
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

import sqlalchemy as sa
from sqlalchemy.orm import exc as orm_exc

from solum.objects import app as abstract
from solum.objects.sqlalchemy import models as sql


class App(sql.Base, abstract.App):
    """Represent an app in sqlalchemy."""

    __tablename__ = 'app'
    __resource__ = 'apps'
    __table_args__ = sql.table_args()

    id = sa.Column(sa.String(36), primary_key=True)
    deleted = sa.Column(sa.Boolean, default=False)
    project_id = sa.Column(sa.String(36))
    user_id = sa.Column(sa.String(36))

    languagepack = sa.Column(sa.String(1024))
    stack_id = sa.Column(sa.String(36))

    name = sa.Column(sa.String(length=100))
    description = sa.Column(sa.String(length=255))
    ports = sa.Column(sql.YAMLEncodedDict(1024))
    source = sa.Column(sql.YAMLEncodedDict(1024))
    workflow_config = sa.Column(sql.YAMLEncodedDict(1024))
    trigger_uuid = sa.Column(sa.String(length=36))
    trigger_actions = sa.Column(sql.YAMLEncodedDict(1024))
    trust_id = sa.Column(sa.String(255))
    trust_user = sa.Column(sa.String(256))
    status = sa.Column(sa.String(36))
    app_url = sa.Column(sa.String(1024))
    raw_content = sa.Column(sa.String(2048))
    scale_config = sa.Column(sql.JSONEncodedDict(1024))

    def _non_updatable_fields(self):
        return set(('id', 'project_id'))

    @classmethod
    def get_by_uuid(cls, context, item_uuid):
        app = cls.get_by_id(context, item_uuid)
        return app

    @classmethod
    def get_by_trigger_id(cls, context, trigger_id):
        try:
            session = sql.Base.get_session()
            return session.query(cls).filter_by(trigger_uuid=trigger_id).one()
        except sa.orm.exc.NoResultFound:
            cls._raise_trigger_not_found(trigger_id)

    @classmethod
    def get_all_by_lp(cls, context, lp):
        session = sql.SolumBase.get_session()
        apps = []
        with session.begin():
            query = session.query(cls).filter_by(languagepack=lp)
            apps = sql.filter_by_project(context, query).all()
            return apps

    @classmethod
    @sql.retry
    def update_and_save(cls, context, id_or_uuid, data):
        try:
            session = sql.SolumBase.get_session()
            with session.begin():
                query = session.query(cls).filter_by(id=id_or_uuid)
                obj = sql.filter_by_project(context, query).one()
                if obj._is_updatable():
                    obj.update(data)
                    session.merge(obj)
            return obj
        except orm_exc.NoResultFound:
            cls._raise_not_found(id_or_uuid)


class AppList(abstract.AppList):
    """Represent a list of apps in sqlalchemy."""

    @classmethod
    def get_all(cls, context):
        return AppList(sql.model_query(context, App))
