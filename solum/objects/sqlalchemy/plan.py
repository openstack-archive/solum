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

from oslo_log import log as logging
import sqlalchemy as sa

from solum.common import exception
from solum.objects import plan as abstract
from solum.objects.sqlalchemy import models as sql


LOG = logging.getLogger(__name__)


class Plan(sql.Base, abstract.Plan):
    """Represent a plan in sqlalchemy."""

    __resource__ = 'plans'
    __tablename__ = 'plan'
    __table_args__ = sql.table_args()

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    uuid = sa.Column(sa.String(36))
    project_id = sa.Column(sa.String(36))
    user_id = sa.Column(sa.String(36))
    name = sa.Column(sa.String(255), nullable=False)
    description = sa.Column(sa.String(255))
    raw_content = sa.Column(sql.YAMLEncodedDict(2048))
    trigger_id = sa.Column(sa.String(36))
    trust_id = sa.Column(sa.String(255))
    username = sa.Column(sa.String(256))

    @classmethod
    def _raise_trigger_not_found(cls, item_id):
        """Raise a NotFound exception."""
        raise exception.ResourceNotFound(id=item_id, name='trigger')

    @classmethod
    def get_by_trigger_id(cls, context, trigger_id):
        try:
            session = sql.Base.get_session()
            return session.query(cls).filter_by(trigger_id=trigger_id).one()
        except sa.orm.exc.NoResultFound:
            cls._raise_trigger_not_found(trigger_id)

    @classmethod
    def get_by_uuid(cls, context, app_id):
        try:
            session = sql.Base.get_session()
            return session.query(cls).filter_by(uuid=app_id).one()
        except sa.orm.exc.NoResultFound as e:
            LOG.exception(e)
            raise exception.ResourceNotFound(id=app_id, name='plan')

    def _non_updatable_fields(self):
        return set(('uuid', 'id', 'project_id'))

    def refined_content(self):
        if self.raw_content and self.uuid:
            self.raw_content['uuid'] = self.uuid
        return self.raw_content


class PlanList(abstract.PlanList):
    """Represent a list of plans in sqlalchemy."""

    @classmethod
    def get_all(cls, context):
        return PlanList(sql.model_query(context, Plan))
