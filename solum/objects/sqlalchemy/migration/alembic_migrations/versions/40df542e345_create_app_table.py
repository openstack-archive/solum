# Copyright 2014 - Rackspace
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

"""Create app table

Revision ID: 40df542e345
Revises: 5583c6e70156
Create Date: 2015-05-19 18:52:34.825827

"""
from alembic import op
import sqlalchemy as sa

from solum.objects.sqlalchemy import models

from oslo_utils import timeutils

# revision identifiers, used by Alembic.
revision = '40df542e345'
down_revision = '1393c21ea82c'


def upgrade():
    op.create_table(
        'app',
        sa.Column('id', sa.String(length=36), primary_key=True,
                  nullable=False),
        sa.Column('created_at', sa.DateTime, default=timeutils.utcnow),
        sa.Column('updated_at', sa.DateTime, onupdate=timeutils.utcnow),
        sa.Column('deleted', sa.Boolean, default=False, nullable=False),
        sa.Column('project_id', sa.String(length=36)),
        sa.Column('user_id', sa.String(length=36)),

        sa.Column('languagepack', sa.String(length=100), nullable=False),
        sa.Column('stack_id', sa.String(length=36)),

        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.String(length=255), nullable=False),
        sa.Column('ports', models.YAMLEncodedDict(1024)),
        sa.Column('source', models.YAMLEncodedDict(1024)),
        sa.Column('workflow_config', models.YAMLEncodedDict(1024)),
        sa.Column('trigger_uuid', sa.String(length=36)),
        sa.Column('trigger_actions', models.YAMLEncodedDict(1024)),
        sa.Column('trust_id', sa.String(length=255)),
        sa.Column('trust_user', sa.String(length=256)),
        )


def downgrade():
    op.drop_table('app')
