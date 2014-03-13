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

"""update lp table to match model

Revision ID: 23f2a946d20e
Revises: 9012e1a6ff1
Create Date: 2014-03-13 11:07:00.568996

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '23f2a946d20e'
down_revision = '9012e1a6ff1'


def upgrade():
    op.add_column('language_pack', sa.Column('language_implementation',
                                             sa.String(length=100),
                                             nullable=True))
    op.add_column('language_pack', sa.Column('language_pack_type',
                                             sa.String(length=100),
                                             nullable=True))
    op.drop_column('language_pack', 'language_impl')
    op.drop_column('language_pack', 'type')


def downgrade():
    op.add_column('language_pack', sa.Column('language_impl',
                                             sa.String(length=100),
                                             nullable=True))
    op.add_column('language_pack', sa.Column('type',
                                             sa.String(length=100),
                                             nullable=True))
    op.drop_column('language_pack', 'language_implementation')
    op.drop_column('language_pack', 'language_pack_type')
