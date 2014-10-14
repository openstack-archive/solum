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

"""add artifact_type to image table

Revision ID: 3a615b3b2eae
Revises: 450600086a09
Create Date: 2014-10-13 17:25:04.880051

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '3a615b3b2eae'
down_revision = '450600086a09'


def upgrade():
    op.add_column('image', sa.Column('artifact_type', sa.String(length=36)))


def downgrade():
    op.drop_column('image', 'artifact_type')
