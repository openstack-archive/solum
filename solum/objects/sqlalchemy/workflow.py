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
from sqlalchemy.sql import text

from solum.objects.sqlalchemy import assembly
from solum.objects.sqlalchemy import component
from solum.objects.sqlalchemy import image
from solum.objects.sqlalchemy import models as sql
from solum.objects.sqlalchemy import plan
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
    assembly = sa.Column(sa.Integer())
    status = sa.Column(sa.String(36))
    result = sa.Column(sa.Text)

    def _non_updatable_fields(self):
        return set(('id', 'project_id'))

    @classmethod
    def get_by_assembly_id(cls, assembly_id):
        try:
            session = sql.Base.get_session()
            result = session.query(Workflow)
            result = result.filter(Workflow.assembly == assembly_id)
            return result.one()
        except orm_exc.NoResultFound:
            cls._raise_not_found(assembly_id)

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

    @classmethod
    @sql.retry
    def insert(cls, context, db_obj):
        try:
            ss = sql.Base.get_session()
            with ss.begin():
                s = text("select max(wf_id) as max_wf_id "
                         "from workflow where app_id like :app")
                res = ss.execute(s, params=dict(app=db_obj.app_id)).fetchone()
                if res.max_wf_id:
                    db_obj.wf_id = res.max_wf_id + 1
                else:
                    db_obj.wf_id = 1
                db_obj.create(context)
        except orm_exc.NoResultFound:
            cls._raise_not_found(db_obj.app_id)

    @classmethod
    @sql.retry
    def destroy(cls, app_id):
        # Delete relevant plan, assembly, component on workflow delete
        try:
            session = sql.Base.get_session()
            plan_id = None
            image_name = None
            with session.begin():
                wfs = session.query(cls).filter_by(app_id=app_id).all()
                for wf_obj in wfs:
                    asm = session.query(assembly.Assembly).filter_by(
                        id=wf_obj.assembly).one()
                    plan_id = asm.plan_id
                    image_name = asm.name
                    # delete component
                    session.query(component.Component).filter_by(
                        assembly_id=wf_obj.assembly).delete()
                    # delete assembly
                    session.query(assembly.Assembly).filter_by(
                        id=wf_obj.assembly).delete()

                # delete plan
                if not plan_id:
                    plan_id = app_id
                session.query(plan.Plan).filter_by(id=plan_id).delete()
                # delete workflows
                session.query(cls).filter_by(app_id=app_id).delete()
                # delete image
                if image_name:
                    session.query(image.Image).filter_by(
                        name=image_name).delete()
        except orm_exc.NoResultFound:
            cls._raise_not_found(app_id)


class WorkflowList(abstract.WorkflowList):
    """Represent a list of app workflows in sqlalchemy."""

    @classmethod
    def get_all(cls, context, app_id=None):
        wfs = sql.model_query(context, Workflow)
        if app_id is not None:
            wfs = wfs.filter_by(app_id=app_id)
        return WorkflowList(wfs)
