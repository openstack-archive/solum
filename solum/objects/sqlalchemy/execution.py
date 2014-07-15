# Copyright 2014 - Rackspace Hosting
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

from solum.objects import execution as abstract
from solum.objects.sqlalchemy import models as sql


class Execution(sql.Base, abstract.Execution):
    """Represent an execution in sqlalchemy."""

    __tablename__ = 'execution'
    __resource__ = 'executions'
    __table_args__ = sql.table_args()

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    uuid = sa.Column(sa.String(36))
    pipeline_id = sa.Column(sa.Integer, sa.ForeignKey('pipeline.id'))


class ExecutionList(abstract.ExecutionList):
    """Represent a list of executions in sqlalchemy."""

    @classmethod
    def get_all(cls, context):
        return ExecutionList(sql.model_query(context, Execution))
