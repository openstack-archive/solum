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

from solum.objects.sqlalchemy import models as sql
from solum.objects import workflow as abstract


class Workflow(sql.Base, abstract.Workflow):
    """Represent an app workflow in sqlalchemy."""

    __tablename__ = 'workflow'
    __resource__ = 'workflows'
    __table_args__ = sql.table_args()

    id = sa.Column(sa.String(36), primary_key=True)
    deleted = sa.Column(sa.Boolean, default=False)
    project_id = sa.Column(sa.String(36))
    user_id = sa.Column(sa.String(36))

    app_id = sa.Column(sa.String(36))
    wf_id = sa.Column(sa.Integer())
    source = sa.Column(sql.YAMLEncodedDict(1024))
    config = sa.Column(sql.YAMLEncodedDict(1024))
    actions = sa.Column(sql.YAMLEncodedDict(1024))
    status = sa.Column(sa.String(length=36))

    def _non_updatable_fields(self):
        return set(('id', 'project_id'))

    @classmethod
    def get_by_uuid(cls, context, item_uuid):
        return cls.get_by_id(context, item_uuid)

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


class WorkflowList(abstract.WorkflowList):
    """Represent a list of app workflows in sqlalchemy."""

    @classmethod
    def get_all(cls, context, app_id=None):
        wfs = sql.model_query(context, Workflow)
        if app_id is not None:
            wfs = wfs.filter_by(app_id=app_id)
        return WorkflowList(wfs)
