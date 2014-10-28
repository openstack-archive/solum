# Copyright 2014 - Rackspace, Inc.
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
from sqlalchemy.orm import exc

from solum.objects import parameter as abstract
from solum.objects.sqlalchemy import models as sql


class Parameter(sql.Base, abstract.Parameter):
    """Represent a parameter in sqlalchemy."""

    __resource__ = 'parameters'
    __tablename__ = 'parameter'
    __table_args__ = sql.table_args()

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    plan_id = sa.Column(sa.Integer, sa.ForeignKey('plan.id'),
                        nullable=False)
    user_defined_params = sa.Column(sql.YAMLEncodedDict(65535))
    sys_defined_params = sa.Column(sql.YAMLEncodedDict(65535))

    @classmethod
    def get_by_plan_id(cls, context, p_id):
        try:
            session = sql.SolumBase.get_session()
            return session.query(cls).filter_by(plan_id=p_id).one()
        except exc.NoResultFound:
            return None


class ParameterList(abstract.ParameterList):
    """Represent a list of parameters in sqlalchemy."""

    @classmethod
    def get_all(cls, context):
        return ParameterList(sql.model_query(context, Parameter))
