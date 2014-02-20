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

"""Add extension

Revision ID: 1767df1e2659
Revises: 3d1c8e21f103
Create Date: 2014-02-05 16:32:45.660619

"""
from alembic import op
import sqlalchemy as sa

from solum.openstack.common import timeutils

# revision identifiers, used by Alembic.
revision = '1767df1e2659'
down_revision = '3d1c8e21f103'


def upgrade():
    op.create_table(
        'extension',
        sa.Column('id', sa.Integer, primary_key=True, nullable=False),
        sa.Column('uuid', sa.String(length=36), nullable=False),
        sa.Column('created_at', sa.DateTime, default=timeutils.utcnow),
        sa.Column('updated_at', sa.DateTime, onupdate=timeutils.utcnow),
        sa.Column('project_id', sa.String(36)),
        sa.Column('user_id', sa.String(36)),
        sa.Column('description', sa.String(255)),
        sa.Column('name', sa.String(100)),
        sa.Column('version', sa.String(16)),
        sa.Column('documentation', sa.String(255)),
        # NOTE(stannie): tags will be added in a dedicated table
    )


def downgrade():
    op.drop_table('extension')
