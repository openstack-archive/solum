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

"""merge plan and application

Revision ID: 4d72260e56e
Revises: 37d6ad94f2ce
Create Date: 2014-02-10 15:47:22.533219

"""
from alembic import op
import sqlalchemy as sa

from solum.openstack.common import timeutils

# revision identifiers, used by Alembic.
revision = '4d72260e56e'
down_revision = '37d6ad94f2ce'


def upgrade():
    op.add_column('plan', sa.Column('glance_id', sa.String(36)))
    op.add_column('plan', sa.Column('name', sa.String(255)))
    op.drop_table('application')


def downgrade():
    op.create_table(
        'application',
        sa.Column('id', sa.Integer, primary_key=True, nullable=False),
        sa.Column('uuid', sa.String(length=36), nullable=False),
        sa.Column('created_at', sa.DateTime, default=timeutils.utcnow),
        sa.Column('updated_at', sa.DateTime, onupdate=timeutils.utcnow),
        sa.Column('name', sa.String(255)),
        sa.Column('glance_id', sa.String(36)),
    )
    op.drop_column('plan', 'glance_id')
    op.drop_column('plan', 'name')
