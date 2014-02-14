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

"""Add sensor

Revision ID: 3d1c8e21f103
Revises: a42f578cef8
Create Date: 2014-02-06 15:15:19.447394

"""
from alembic import op
import sqlalchemy as sa

from solum.openstack.common import timeutils

# revision identifiers, used by Alembic.
revision = '3d1c8e21f103'
down_revision = '46ffedad6d56'


def upgrade():
    op.create_table(
        'sensor',
        sa.Column('id', sa.Integer, primary_key=True, nullable=False),
        sa.Column('uuid', sa.String(length=36), nullable=False),
        sa.Column('created_at', sa.DateTime, default=timeutils.utcnow),
        sa.Column('updated_at', sa.DateTime, onupdate=timeutils.utcnow),
        sa.Column('project_id', sa.String(length=36)),
        sa.Column('user_id', sa.String(length=36)),
        sa.Column('name', sa.String(255)),
        sa.Column('sensor_type', sa.String(255)),
        sa.Column('value', sa.String(255)),
        sa.Column('timestamp', sa.DateTime),
        sa.Column('description', sa.String(255)),
        sa.Column('documentation', sa.String(255)),
        sa.Column('target_resource', sa.String(255)),
    )


def downgrade():
    op.drop_table('sensor')
