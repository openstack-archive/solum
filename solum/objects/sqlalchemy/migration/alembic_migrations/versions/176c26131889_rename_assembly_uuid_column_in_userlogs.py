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

"""Rename assembly_uuid column in userlogs

Revision ID: 176c26131889
Revises: 2c058b5051e4
Create Date: 2015-02-06 19:35:19.658096

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '176c26131889'
down_revision = '2c058b5051e4'


def upgrade():
    op.alter_column('userlogs', 'assembly_uuid',
                    new_column_name='resource_uuid',
                    existing_nullable=False,
                    existing_type=sa.String(36))
    op.add_column('userlogs',
                  sa.Column('resource_type', sa.String(length=36)))


def downgrade():
    op.alter_column('userlogs', 'resource_uuid',
                    new_column_name='assembly_uuid',
                    existing_nullable=False,
                    existing_type=sa.String(36))
    op.drop_column('userlogs', 'resource_type')
