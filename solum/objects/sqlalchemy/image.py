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

from oslo_config import cfg
from oslo_log import log as logging
from oslo_utils import uuidutils
import sqlalchemy as sa
from sqlalchemy.orm import exc

from solum.objects import image as abstract
from solum.objects.sqlalchemy import models as sql

cfg.CONF.import_opt('operator_project_id',
                    'solum.api.handlers.language_pack_handler',
                    group='api')

operator_id = cfg.CONF.api.operator_project_id

LOG = logging.getLogger(__name__)


class Image(sql.Base, abstract.Image):
    """Represent a image in sqlalchemy."""

    __tablename__ = 'image'
    __resource__ = 'images'
    __table_args__ = sql.table_args()

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    uuid = sa.Column(sa.String(36), nullable=False)
    name = sa.Column(sa.String(100))
    source_uri = sa.Column(sa.String(1024))
    source_format = sa.Column(sa.String(36))
    description = sa.Column(sa.String(255))
    project_id = sa.Column(sa.String(36))
    user_id = sa.Column(sa.String(36))
    tags = sa.Column(sa.Text)
    status = sa.Column(sa.String(12))
    base_image_id = sa.Column(sa.String(36))
    created_image_id = sa.Column(sa.String(36))
    image_format = sa.Column(sa.String(12))
    artifact_type = sa.Column(sa.String(36))
    external_ref = sa.Column(sa.String(1024))
    docker_image_name = sa.Column(sa.String(512))

    @classmethod
    def get_num_of_lps(cls, context):
        try:
            session = Image.get_session()
            oper_result = session.query(cls).filter_by(
                project_id=context.project_id, status='READY')
            cnt = oper_result.count()
            return cnt
        except exc.NoResultFound:
            LOG.debug("Exception encountered in getting count of number"
                      " of languagepacks")

    @classmethod
    def get_lp_by_name_or_uuid(cls, context, name_or_uuid,
                               include_operators_lp=False):
        if uuidutils.is_uuid_like(name_or_uuid):
            try:
                session = Image.get_session()
                result = session.query(cls).filter_by(
                    artifact_type='language_pack', uuid=name_or_uuid)
                if include_operators_lp is True:
                    project_id = context.project_id
                    result = result.filter(
                        Image.project_id.in_([operator_id, project_id]))
                    return result.one()
                else:
                    return sql.filter_by_project(context, result).one()
            except exc.NoResultFound:
                return cls.get_by_name(context, name_or_uuid,
                                       include_operators_lp)
        else:
            return cls.get_by_name(context, name_or_uuid, include_operators_lp)

    @classmethod
    def get_by_name(cls, context, name, include_operators_lp=False):
        try:
            session = Image.get_session()
            result = session.query(cls).filter_by(
                artifact_type='language_pack', name=name)
            if include_operators_lp is True:
                result = result.filter(
                    Image.project_id.in_([operator_id, context.project_id]))
                return result.one()
            else:
                return sql.filter_by_project(context, result).one()
        except exc.NoResultFound:
            cls._raise_not_found(name)

    @classmethod
    def get_all_languagepacks(cls, context):
        """Return all images that are languagepacks."""
        session = Image.get_session()
        result = session.query(cls)
        result = result.filter_by(artifact_type='language_pack')
        result = sql.filter_by_project(context, result)

        # Include Languagepacks that have been created by the operator, and
        # are in the 'READY' state.
        # The operator LP is identified based on the operator_project_id
        # config setting in solum.conf
        oper_result = session.query(cls)
        oper_result = oper_result.filter_by(artifact_type='language_pack')
        oper_result = oper_result.filter_by(status='READY')
        oper_result = oper_result.filter_by(project_id=operator_id)

        return result.union(oper_result).all()


class ImageList(abstract.ImageList):
    """Represent a list of images in sqlalchemy."""

    @classmethod
    def get_all(cls, context):
        """Return all images."""
        return ImageList(sql.model_query(context, Image))

    @classmethod
    def get_all_languagepacks(cls, context):
        """Return all images that are languagepacks."""
        return ImageList(sql.model_query(
            context, Image).filter_by(artifact_type='language_pack'))
