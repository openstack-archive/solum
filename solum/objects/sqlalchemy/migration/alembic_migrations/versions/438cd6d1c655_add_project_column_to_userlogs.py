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

"""add project column to userlogs

Revision ID: 438cd6d1c655
Revises: 269f9da4b38e
Create Date: 2014-11-19 19:25:21.654009

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '438cd6d1c655'
down_revision = '269f9da4b38e'


def upgrade():
    op.add_column('userlogs',
                  sa.Column('project_id', sa.String(length=36)))


def downgrade():
    op.drop_column('userlogs', 'project_id')
