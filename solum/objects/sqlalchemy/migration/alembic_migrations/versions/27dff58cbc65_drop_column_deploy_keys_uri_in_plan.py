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

"""drop column deploy_keys_uri in plan

Revision ID: 27dff58cbc65
Revises: 438cd6d1c655
Create Date: 2015-01-03 04:23:08.078712

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '27dff58cbc65'
down_revision = '438cd6d1c655'


def upgrade():
    op.drop_column('plan', 'deploy_keys_uri')


def downgrade():
    op.add_column('plan', sa.Column('deploy_keys_uri', sa.String(length=1024)))
