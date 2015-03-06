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

"""rename image state column to status

Revision ID: 1f57763d7871
Revises: 2f15f41cd87f
Create Date: 2015-03-09 16:46:44.406091

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '1f57763d7871'
down_revision = '2f15f41cd87f'


def upgrade():
    op.alter_column('image', 'state',
                    new_column_name='status',
                    existing_nullable=True,
                    existing_type=sa.String(36))


def downgrade():
    op.alter_column('image', 'status',
                    new_column_name='state',
                    existing_nullable=True,
                    existing_type=sa.String(36))
