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

"""Add user logs table

Revision ID: 450600086a09
Revises: 498adc6185ae
Create Date: 2014-09-29 20:43:55.544682

"""
from alembic import op
from oslo_utils import timeutils
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '450600086a09'
down_revision = '498adc6185ae'


def upgrade():
    op.create_table(
        'userlogs',
        sa.Column('id', sa.Integer, primary_key=True, nullable=False),
        sa.Column('created_at', sa.DateTime, default=timeutils.utcnow,
                  nullable=False),
        sa.Column('updated_at', sa.DateTime, default=timeutils.utcnow,
                  nullable=False),
        sa.Column('assembly_uuid', sa.String(36), nullable=False),
        sa.Column('location', sa.String(255), nullable=False),
        sa.Column('strategy', sa.String(255), nullable=False),
        sa.Column('strategy_info', sa.String(1024), nullable=False),
        )


def downgrade():
    op.drop_table('userlogs')
