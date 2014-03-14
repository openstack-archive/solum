# Copyright 2014 - Rackspace Hosting
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

"""add status to assembly

Revision ID: 44fcd06e4009
Revises: 23f2a946d20e
Create Date: 2014-03-13 16:29:01.736249

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '44fcd06e4009'
down_revision = '23f2a946d20e'


def upgrade():
    op.add_column('assembly', sa.Column('status', sa.String(length=36)))


def downgrade():
    op.drop_column('assembly', 'status')
