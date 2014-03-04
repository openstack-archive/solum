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

"""add image table

Revision ID: 3d69d7ff26cb
Revises: 365ff074069c
Create Date: 2014-02-13 17:34:16.133515

"""
from alembic import op
import sqlalchemy as sa

from solum.openstack.common import timeutils

# revision identifiers, used by Alembic.
revision = '3d69d7ff26cb'
down_revision = '365ff074069c'


def upgrade():
    op.create_table(
        'image',
        sa.Column('id', sa.Integer, primary_key=True, nullable=False),
        sa.Column('uuid', sa.String(36), nullable=False),
        sa.Column('created_at', sa.DateTime, default=timeutils.utcnow),
        sa.Column('updated_at', sa.DateTime, onupdate=timeutils.utcnow),
        sa.Column('name', sa.String(100)),
        sa.Column('description', sa.String(255)),
        sa.Column('source_uri', sa.String(255)),
        sa.Column('project_id', sa.String(36)),
        sa.Column('user_id', sa.String(36)),
        sa.Column('tags', sa.Text),
        sa.Column('state', sa.String(12)),
    )


def downgrade():
    op.drop_table('image')
