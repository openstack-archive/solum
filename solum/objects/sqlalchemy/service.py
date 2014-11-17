# Copyright 2014 - Rackspace US, Inc.
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

from solum.objects import service as abstract
from solum.objects.sqlalchemy import models as sql


class Service(sql.Base, abstract.Service):
    """Represent a service in sqlalchemy."""

    __resource__ = 'services'
    __tablename__ = 'service'
    __table_args__ = sql.table_args()

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    uuid = sa.Column(sa.String(36), nullable=False)
    name = sa.Column(sa.String(100))
    description = sa.Column(sa.String(255))
    project_id = sa.Column(sa.String(36))
    user_id = sa.Column(sa.String(36))
    service_type = sa.Column(sa.String(100))
    read_only = sa.Column(sa.Boolean, default=False)
    tags = sa.Column(sa.Text)

    def _non_updatable_fields(self):
        return set(('uuid', 'id', 'project_id'))


class ServiceList(abstract.ServiceList):
    """Represent a list of services in sqlalchemy."""

    @classmethod
    def get_all(cls, context):
        return ServiceList(sql.model_query(context, Service))
