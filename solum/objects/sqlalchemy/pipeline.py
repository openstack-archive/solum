# Copyright 2014 - Rackspace Hosting
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

import sqlalchemy

from solum.common import exception
from solum import objects
from solum.objects import pipeline as abstract
from solum.objects.sqlalchemy import models as sql


class Pipeline(sql.Base, abstract.Pipeline):
    """Represent an pipeline in sqlalchemy."""

    __resource__ = 'pipelines'
    __tablename__ = 'pipeline'
    __table_args__ = sql.table_args()

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True,
                           autoincrement=True)
    uuid = sqlalchemy.Column(sqlalchemy.String(36))
    project_id = sqlalchemy.Column(sqlalchemy.String(36))
    user_id = sqlalchemy.Column(sqlalchemy.String(36))
    name = sqlalchemy.Column(sqlalchemy.String(100))
    description = sqlalchemy.Column(sqlalchemy.String(255))
    tags = sqlalchemy.Column(sqlalchemy.Text)
    workbook_name = sqlalchemy.Column(sqlalchemy.String(255))
    plan_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey('plan.id'),
                                nullable=False)
    trigger_id = sqlalchemy.Column(sqlalchemy.String(36))
    trust_id = sqlalchemy.Column(sqlalchemy.String(255))

    @property
    def plan_uuid(self):
        return objects.registry.Plan.get_by_id(None, self.plan_id).uuid

    @plan_uuid.setter
    def plan_uuid(self, value):
        plan = objects.registry.Plan.get_by_uuid(None, value)
        self.plan_id = plan.id

    @property
    def _extra_keys(self):
        return ['plan_uuid']

    @classmethod
    def get_by_trigger_id(cls, context, trigger_id):
        try:
            session = sql.Base.get_session()
            return session.query(cls).filter_by(trigger_id=trigger_id).one()
        except sqlalchemy.orm.exc.NoResultFound:
            raise exception.ResourceNotFound(id=trigger_id, name='trigger')


class PipelineList(abstract.PipelineList):
    """Represent a list of pipelines in sqlalchemy."""

    @classmethod
    def get_all(cls, context):
        return PipelineList(sql.model_query(context, Pipeline))
