# Copyright 2015 - Rackspace
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

"""Add image id to assembly table

Revision ID: 1393c21ea82c
Revises: 452f34e8ea3
Create Date: 2015-05-28 22:31:45.336763

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '1393c21ea82c'
down_revision = '452f34e8ea3'


def upgrade():
    op.add_column('assembly',
                  sa.Column('image_id', sa.Integer))


def downgrade():
    op.drop_column('assembly', 'image_id')
