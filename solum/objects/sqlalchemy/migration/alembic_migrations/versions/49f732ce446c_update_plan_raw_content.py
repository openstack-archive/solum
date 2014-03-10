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

"""Update plan raw content

Revision ID: 49f732ce446c
Revises: 2e60bd23410d
Create Date: 2014-03-05 15:24:41.791610

"""

from alembic import op
import sqlalchemy as sa

from solum.objects.sqlalchemy import models

# revision identifiers, used by Alembic.
revision = '49f732ce446c'
down_revision = '2e60bd23410d'


def upgrade():
    op.alter_column('plan', 'raw_content', type_=models.JSONEncodedDict(2048))


def downgrade():
    op.alter_column('plan', 'raw_content', type_=sa.Text)
