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

"""add workflow column to assembly table

Revision ID: 2f15f41cd87f
Revises: 176c26131889
Create Date: 2015-03-04 23:10:57.979224

"""
from alembic import op
import sqlalchemy as sa

from solum.objects.sqlalchemy import models

# revision identifiers, used by Alembic.
revision = '2f15f41cd87f'
down_revision = '176c26131889'


def upgrade():
    op.add_column('assembly',
                  sa.Column('workflow', models.YAMLEncodedDict(1024)))


def downgrade():
    op.drop_column('assembly', 'workflow')
