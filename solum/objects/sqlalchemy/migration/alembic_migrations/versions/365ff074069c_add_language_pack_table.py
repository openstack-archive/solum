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

"""Add language_pack table

Revision ID: 365ff074069c
Revises: 27e7701946fe
Create Date: 2014-02-03 15:51:20.819539

"""
from alembic import op
import sqlalchemy as sa

from solum.objects.sqlalchemy import models
from solum.openstack.common import timeutils

# revision identifiers, used by Alembic.
revision = '365ff074069c'
down_revision = '27e7701946fe'


def upgrade():
    op.create_table(
        'language_pack',
        sa.Column('id', sa.Integer, primary_key=True, nullable=False),
        sa.Column('uuid', sa.String(36), nullable=False),
        sa.Column('created_at', sa.DateTime, default=timeutils.utcnow),
        sa.Column('updated_at', sa.DateTime, onupdate=timeutils.utcnow),
        sa.Column('name', sa.String(100)),
        sa.Column('type', sa.String(100)),
        sa.Column('description', sa.String(255)),
        sa.Column('project_id', sa.String(36)),
        sa.Column('user_id', sa.String(36)),
        sa.Column('language_impl', sa.String(100)),
        sa.Column('tags', sa.Text),
        sa.Column('attr_blob', models.JSONEncodedDict(255)),
        sa.Column('service_id', sa.Integer, sa.ForeignKey('service.id'),
                  nullable=False),
        )

    op.create_table(
        'compiler_versions',
        sa.Column('id', sa.Integer, primary_key=True, nullable=False),
        sa.Column('uuid', sa.String(36), nullable=False),
        sa.Column('created_at', sa.DateTime, default=timeutils.utcnow),
        sa.Column('updated_at', sa.DateTime, onupdate=timeutils.utcnow),
        sa.Column('version', sa.String(36), nullable=False),
        sa.Column('language_pack_id', sa.Integer,
                  sa.ForeignKey('language_pack.id'), nullable=False),
        )

    op.create_table(
        'os_platform',
        sa.Column('id', sa.Integer, primary_key=True, nullable=False),
        sa.Column('uuid', sa.String(36), nullable=False),
        sa.Column('created_at', sa.DateTime, default=timeutils.utcnow),
        sa.Column('updated_at', sa.DateTime, onupdate=timeutils.utcnow),
        sa.Column('OS', sa.String(36), nullable=False),
        sa.Column('version', sa.String(36), nullable=False),
        sa.Column('language_pack_id', sa.Integer,
                  sa.ForeignKey('language_pack.id'), nullable=False),
        )


def downgrade():
    op.drop_table('language_pack')
    op.drop_table('compiler_versions')
    op.drop_table('os_platform')
