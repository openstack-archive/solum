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

"""add missing description field

Revision ID: 27e7701946fe
Revises: 396a439167dc
Create Date: 2014-02-28 16:57:14.662645

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '27e7701946fe'
down_revision = '396a439167dc'


def upgrade():
    op.add_column('plan', sa.Column('description', sa.String(length=255)))


def downgrade():
    op.drop_column('plan', 'description')
