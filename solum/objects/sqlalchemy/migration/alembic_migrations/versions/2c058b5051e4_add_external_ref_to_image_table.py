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

"""add external_ref to image table

Revision ID: 2c058b5051e4
Revises: 27dff58cbc65
Create Date: 2015-01-05 20:07:41.936667

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '2c058b5051e4'
down_revision = '27dff58cbc65'


def upgrade():
    op.add_column('image',
                  sa.Column('external_ref', sa.String(length=1024)))


def downgrade():
    op.drop_column('image', 'external_ref')
