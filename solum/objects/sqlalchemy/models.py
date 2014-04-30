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

import json
import six

from oslo.config import cfg
from sqlalchemy.ext import declarative
from sqlalchemy.orm import exc
from sqlalchemy import types

from solum.common import exception
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
        for k in self._extra_keys:
            d[k] = self[k]
        return d

    @classmethod
    def get_session(cls):
        return db_session.get_session(mysql_traditional_mode=True)

    @classmethod
    def get_by_id(cls, context, item_id):
        try:
            session = SolumBase.get_session()
            return session.query(cls).filter_by(id=item_id).one()
        except exc.NoResultFound:
            cls._raise_not_found(item_id)

    @classmethod
    def get_by_uuid(cls, context, item_uuid):
        try:
            session = SolumBase.get_session()
            return session.query(cls).filter_by(uuid=item_uuid).one()
        except exc.NoResultFound:
            cls._raise_not_found(item_uuid)

    @classmethod
    def _raise_duplicate_object(cls):
        if hasattr(cls, '__resource__'):
            raise exception.ResourceExists(name=cls.__resource__)
        else:
            raise exception.ObjectNotUnique(name=cls.__tablename__)

    def _non_updatable_fields(self):
        return set(('uuid', 'id'))

    def _lazyhasattr(self, name):
        return any(name in d for d in (self.__dict__,
                                       self.__class__.__dict__))

    def update(self, data):
        for field in set(six.iterkeys(data)) - self._non_updatable_fields():
            if self._lazyhasattr(field):
                setattr(self, field, data[field])

    def save(self, context):
        if objects.transition_schema():
            self.add_forward_schema_changes()

        session = SolumBase.get_session()
        with session.begin():
            session.merge(self)

    def create(self, context):
        session = SolumBase.get_session()
        try:
            with session.begin():
                session.add(self)
        except (db_exc.DBDuplicateEntry):
            self.__class__._raise_duplicate_object()

    def destroy(self, context):
        session = SolumBase.get_session()
        with session.begin():
            session.query(self.__class__).filter_by(
                id=self.id).delete()

    @classmethod
    def _raise_not_found(cls, item_id):
        """Raise a not found exception."""
        if hasattr(cls, '__resource__'):
            raise exception.ResourceNotFound(name=cls.__resource__, id=item_id)
        else:
            raise exception.ObjectNotFound(name=cls.__tablename__, id=item_id)


Base = declarative.declarative_base(cls=SolumBase)


class JSONEncodedDict(types.TypeDecorator):
    """Represents an immutable structure as a json-encoded string."""

    impl = types.VARCHAR

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = json.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = json.loads(value)
        return value
