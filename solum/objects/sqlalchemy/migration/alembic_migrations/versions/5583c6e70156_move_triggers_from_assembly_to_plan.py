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

"""Move triggers from Assembly to Plan

Revision ID: 5583c6e70156
Revises: 1f57763d7871
Create Date: 2015-03-09 16:31:28.130484

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '5583c6e70156'
down_revision = '1f57763d7871'


def upgrade():
    op.add_column('plan',
                  sa.Column('trigger_id', sa.String(length=36)))
    op.add_column('plan',
                  sa.Column('trust_id', sa.String(length=255)))
    op.add_column('plan',
                  sa.Column('username', sa.String(length=256)))
    op.drop_column('assembly', 'trigger_id')
    op.drop_column('assembly', 'trust_id')


def downgrade():
    op.add_column('assembly',
                  sa.Column('trigger_id', sa.String(length=36)))
    op.add_column('assembly',
                  sa.Column('trust_id', sa.String(length=255)))
    op.drop_column('plan', 'trigger_id')
    op.drop_column('plan', 'trust_id')
    op.drop_column('plan', 'username')
