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

"""create workflow table

Revision ID: 390c6c4aa97b
Revises: 43df309dbf3f
Create Date: 2015-07-06 16:11:55.370993

"""
from alembic import op
import sqlalchemy as sa

from solum.objects.sqlalchemy import models

from oslo_utils import timeutils

# revision identifiers, used by Alembic.
revision = '390c6c4aa97b'
down_revision = '43df309dbf3f'


def upgrade():
    op.create_table(
        'workflow',
        sa.Column('id', sa.String(length=36), primary_key=True,
                  nullable=False),
        sa.Column('created_at', sa.DateTime, default=timeutils.utcnow),
        sa.Column('updated_at', sa.DateTime, onupdate=timeutils.utcnow),
        sa.Column('deleted_at', sa.DateTime, onupdate=timeutils.utcnow),
        sa.Column('deleted', sa.Boolean, default=False, nullable=False),
        sa.Column('project_id', sa.String(length=36)),
        sa.Column('user_id', sa.String(length=36)),

        sa.Column('app_id', sa.String(length=36), nullable=False),
        sa.Column('wf_id', sa.Integer(), nullable=False),
        sa.Column('source', models.YAMLEncodedDict(1024)),
        sa.Column('config', models.YAMLEncodedDict(1024)),
        sa.Column('actions', models.YAMLEncodedDict(1024)),
        sa.Column('status', sa.String(length=36)),
        sa.Column('assembly', sa.Integer)
        )


def downgrade():
    op.drop_table('workflow')
