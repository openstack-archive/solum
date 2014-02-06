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

"""Add service table

Revision ID: 37d6ad94f2ce
Revises: a42f578cef8
Create Date: 2014-01-27 14:25:23.087411

"""
from alembic import op
import sqlalchemy as sa

from solum.openstack.common import timeutils

# revision identifiers, used by Alembic.
revision = '37d6ad94f2ce'
down_revision = 'a42f578cef8'


def upgrade():
    op.create_table(
        'service',
        sa.Column('id', sa.Integer, primary_key=True, nullable=False),
        sa.Column('uuid', sa.String(36), nullable=False),
        sa.Column('created_at', sa.DateTime, default=timeutils.utcnow),
        sa.Column('updated_at', sa.DateTime, onupdate=timeutils.utcnow),
        sa.Column('name', sa.String(100)),
        sa.Column('description', sa.String(255)),
        sa.Column('project_id', sa.String(36)),
        sa.Column('user_id', sa.String(36)),
        sa.Column('service_type', sa.String(100)),
        sa.Column('read_only', sa.Integer, default=0),
        sa.Column('tags', sa.Text),
    )


def downgrade():
    op.drop_table('service')
