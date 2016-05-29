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

"""empty message

Revision ID: 112cfe038dd3
Revises: 390c6c4aa97b
Create Date: 2015-08-20 19:11:01.544203

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '112cfe038dd3'
down_revision = '390c6c4aa97b'


def upgrade():
    op.add_column('app',
                  sa.Column('app_url', sa.String(length=1024)))
    op.add_column('app',
                  sa.Column('status', sa.String(length=36)))


def downgrade():
    op.drop_column('app', 'app_url')
    op.drop_column('app', 'status')
