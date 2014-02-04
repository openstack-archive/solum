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

"""add trigger to assembly

Revision ID: 2e60bd23410d
Revises: 3d69d7ff26cb
Create Date: 2014-02-04 14:15:28.293829

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '2e60bd23410d'
down_revision = '3d69d7ff26cb'


def upgrade():
    op.add_column(
        'assembly',
        sa.Column('trigger_id', sa.String(length=36))
    )


def downgrade():
    op.drop_column('assembly', 'trigger_id')
