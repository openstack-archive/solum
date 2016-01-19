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

Revision ID: 272e7cd352f9
Revises: 2e825c2c80c7
Create Date: 2016-01-19 19:57:57.224831

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '272e7cd352f9'
down_revision = '2e825c2c80c7'


def upgrade():
    op.add_column('workflow', sa.Column('result', sa.Text))


def downgrade():
    op.drop_column('workflow', 'result')
