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

import functools
import json
import time

from oslo_config import cfg
from oslo_db import exception as db_exc
from oslo_db.sqlalchemy import models
from oslo_log import log as logging
from oslo_utils import uuidutils
from sqlalchemy import exc as sqla_exc
from sqlalchemy.ext import declarative
from sqlalchemy.orm import exc as orm_exc
from sqlalchemy import types
from urllib import parse

from solum.common import exception
from solum.common import yamlutils
from solum import objects
from solum.objects import sqlalchemy as object_sqla

LOG = logging.getLogger(__name__)


def retry(fun):
    """Decorator to retry a DB call if certain exception was received."""
    @functools.wraps(fun)
    def _wrapper(*args, **kwargs):
        max_retries = kwargs.pop('max_retries', 3)
        for tries in range(max_retries):
            try:
                return fun(*args, **kwargs)
            except (db_exc.DBDeadlock, orm_exc.StaleDataError,
                    exception.ResourceExists):
                LOG.warning("Failed DB call %s. Retrying %s more times." %
                            (fun.__name__, max_retries - tries - 1))
                if tries + 1 >= max_retries:
                    raise

                time.sleep(0.5)
    return _wrapper


def table_args():
    cfg.CONF.import_opt('connection', 'oslo_db.options',
                        group='database')
    if cfg.CONF.database.connection is None:
        # this is only within some object tests where
        # the object classes are directly imported.
        return None
    engine_name = parse.urlparse(
        cfg.CONF.database.connection).scheme
    if engine_name == 'mysql':
        return {'mysql_engine': 'InnoDB',
                'mysql_charset': "utf8"}
    return None


def filter_by_project(context, query):
    if context is not None:
        if context.is_admin:
            return query
        try:
            query = query.filter_by(project_id=context.project_id)
        except sqla_exc.InvalidRequestError:
            # No project_id column.
            pass
    return query


def model_query(context, model, *args, **kwargs):
    """Query helper.

    :param context: context to query under
    :param session: if present, the session to use
    """

    session = kwargs.get('session') or object_sqla.get_session()

    query = session.query(model, *args)
    return filter_by_project(context, query)


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
        return object_sqla.get_session()

    @classmethod
    def get_by_id(cls, context, item_id):
        try:
            session = SolumBase.get_session()
            result = session.query(cls).filter_by(id=item_id)
            return filter_by_project(context, result).one()
        except orm_exc.NoResultFound:
            cls._raise_not_found(item_id)

    @classmethod
    def get_by_uuid(cls, context, item_uuid):
        try:
            session = SolumBase.get_session()
            result = session.query(cls).filter_by(uuid=item_uuid)
            return filter_by_project(context, result).one()
        except orm_exc.NoResultFound:
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

    def _is_updatable(self):
        return True

    def update(self, data):
        for field in set(data) - self._non_updatable_fields():
            if self._lazyhasattr(field):
                setattr(self, field, data[field])

    @classmethod  # Must be top most
    @retry
    def update_and_save(cls, context, id_or_uuid, data):
        is_uuid = uuidutils.is_uuid_like(id_or_uuid)
        try:
            session = SolumBase.get_session()
            with session.begin():
                if is_uuid:
                    query = session.query(cls).filter_by(uuid=id_or_uuid)
                else:
                    query = session.query(cls).filter_by(id=id_or_uuid)
                obj = filter_by_project(context, query).one()
                if obj._is_updatable():
                    obj.update(data)
                    session.merge(obj)
            return obj
        except orm_exc.NoResultFound:
            cls._raise_not_found(id_or_uuid)

    @retry
    def save(self, context):
        if objects.transition_schema():
            self.add_forward_schema_changes()

        session = SolumBase.get_session()
        with session.begin():
            session.merge(self)

    @retry
    def create(self, context):
        session = SolumBase.get_session()
        try:
            with session.begin():
                session.add(self)
        except (db_exc.DBDuplicateEntry):
            self.__class__._raise_duplicate_object()

    @retry
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

    impl = types.TEXT

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = json.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = json.loads(value)
        return value


class YAMLEncodedDict(types.TypeDecorator):
    """Represents an immutable structure as a yaml-encoded string."""

    impl = types.TEXT

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = yamlutils.dump(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = yamlutils.load(value)
        return value
