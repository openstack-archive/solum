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

"""create parameter table

Revision ID: 586c15b92842
Revises: 3a615b3b2eae
Create Date: 2014-10-28 17:53:56.752062

"""
from alembic import op
import sqlalchemy as sa

from solum.objects.sqlalchemy import models

from oslo_utils import timeutils

# revision identifiers, used by Alembic.
revision = '586c15b92842'
down_revision = '3a615b3b2eae'


def upgrade():
    op.create_table(
        'parameter',
        sa.Column('id', sa.Integer, primary_key=True, nullable=False),
        sa.Column('plan_id', sa.Integer, sa.ForeignKey('plan.id'),
                  nullable=False),
        sa.Column('user_defined_params', models.YAMLEncodedDict(65535)),
        sa.Column('sys_defined_params', models.YAMLEncodedDict(65535)),
        sa.Column('created_at', sa.DateTime, default=timeutils.utcnow),
        sa.Column('updated_at', sa.DateTime, onupdate=timeutils.utcnow),
        )


def downgrade():
    op.drop_table('parameter')
