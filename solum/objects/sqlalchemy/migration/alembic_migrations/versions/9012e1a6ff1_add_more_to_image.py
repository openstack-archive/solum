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

"""add more fields to the image table

Revision ID: 9012e1a6ff1
Revises: 49f732ce446c
Create Date: 2014-03-10 14:24:57.371782

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '9012e1a6ff1'
down_revision = '49f732ce446c'


def upgrade():
    op.add_column('image', sa.Column('base_image_id', sa.String(length=36)))
    op.add_column('image', sa.Column('created_image_id', sa.String(length=36)))
    op.add_column('image', sa.Column('image_format', sa.String(length=12)))
    op.add_column('image', sa.Column('source_format', sa.String(length=12)))
    op.drop_column('plan', 'glance_id')


def downgrade():
    op.add_column('plan', sa.Column('glance_id', sa.String(length=36)))
    op.drop_column('image', 'base_image_id')
    op.drop_column('image', 'created_image_id')
    op.drop_column('image', 'image_format')
    op.drop_column('image', 'source_format')
