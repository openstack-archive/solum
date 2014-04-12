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

from solum.objects import image as abstract
from solum.objects.sqlalchemy import models as sql


class Image(sql.Base, abstract.Image):
    """Represent a image in sqlalchemy."""

    __tablename__ = 'image'
    __resource__ = 'images'
    __table_args__ = sql.table_args()

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    uuid = sa.Column(sa.String(36), nullable=False)
    name = sa.Column(sa.String(100))
    source_uri = sa.Column(sa.String(1024))
    source_format = sa.Column(sa.String(12))
    description = sa.Column(sa.String(255))
    project_id = sa.Column(sa.String(36))
    user_id = sa.Column(sa.String(36))
    tags = sa.Column(sa.Text)
    state = sa.Column(sa.String(12))
    base_image_id = sa.Column(sa.String(36))
    created_image_id = sa.Column(sa.String(36))
    image_format = sa.Column(sa.String(12))


class ImageList(abstract.ImageList):
    """Represent a list of images in sqlalchemy."""

    @classmethod
    def get_all(cls, context):
        return ImageList(sql.model_query(context, Image))
