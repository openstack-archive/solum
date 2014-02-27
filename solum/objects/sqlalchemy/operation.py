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

from solum.objects import operation as abstract
from solum.objects.sqlalchemy import models as sql


class Operation(sql.Base, abstract.Operation):
    """Represent an operation in sqlalchemy."""

    __resource__ = 'operations'
    __tablename__ = 'operation'
    __table_args__ = sql.table_args()

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    uuid = sa.Column(sa.String(36), nullable=False)
    project_id = sa.Column(sa.String(36))
    user_id = sa.Column(sa.String(36))
    name = sa.Column(sa.String(100))
    description = sa.Column(sa.String(255))
    tags = sa.Column(sa.Text)
    documentation = sa.Column(sa.Text)
    target_resource = sa.Column(sa.Text)


class OperationList(abstract.OperationList):
    """Represent a list of operations in sqlalchemy."""

    @classmethod
    def get_all(cls, context):
        return OperationList(sql.model_query(context, Operation))
