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
SQLAlchemy models for application data.
"""

from oslo.config import cfg
from sqlalchemy.ext import declarative

from solum import objects
from solum.openstack.common.db import exception as db_exc
from solum.openstack.common.db.sqlalchemy import models
from solum.openstack.common.db.sqlalchemy import session as db_session
from solum.openstack.common.py3kcompat import urlutils


def table_args():
    engine_name = urlutils.urlparse(cfg.CONF.database.connection).scheme
    if engine_name == 'mysql':
        return {'mysql_engine': 'InnoDB',
                'mysql_charset': "utf8"}
    return None


def model_query(context, model, *args, **kwargs):
    """Query helper.

    :param context: context to query under
    :param session: if present, the session to use
    """

    session = kwargs.get('session') or db_session.get_session(
        mysql_traditional_mode=True)

    query = session.query(model, *args)
    return query


class SolumBase(models.TimestampMixin, models.ModelBase):

    metadata = None

    @classmethod
    def obj_name(cls):
        return cls.__name__

    def as_dict(self):
        d = {}
        for c in self.__table__.columns:
            d[c.name] = self[c.name]
        return d

    @classmethod
    def get_by_id(cls, context, item_id):
        query = db_session.get_session(
            mysql_traditional_mode=True).query(cls).filter_by(id=item_id)
        result = query.first()
        if not result:
            cls._raise_not_found(item_id)
        return result

    def save(self, context):
        if objects.transition_schema():
            self.add_forward_schema_changes()

        session = db_session.get_session(mysql_traditional_mode=True)
        with session.begin():
            session.merge(self)

    def create(self, context):
        session = db_session.get_session(mysql_traditional_mode=True)
        try:
            with session.begin():
                session.add(self)
        except (db_exc.DBDuplicateEntry) as e:
            self.__class__._raise_duplicate_object(e, self)

    def destroy(self, context):
        session = db_session.get_session(mysql_traditional_mode=True)
        with session.begin():
            session.query(self.__class__).\
                filter_by(id=self.id).\
                delete()


Base = declarative.declarative_base(cls=SolumBase)
