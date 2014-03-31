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

"""Add application_uri to assembly

Revision ID: 4ee48e775ad7
Revises: 18b94e085cf9
Create Date: 2014-03-31 03:00:08.128374

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '4ee48e775ad7'
down_revision = '18b94e085cf9'


def upgrade():
    op.add_column('assembly', sa.Column('application_uri',
                                        sa.String(length=1024)))


def downgrade():
    op.drop_column('assembly', 'application_uri')
