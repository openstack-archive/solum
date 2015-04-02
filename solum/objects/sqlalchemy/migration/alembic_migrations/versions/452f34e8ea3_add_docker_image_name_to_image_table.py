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

"""add docker_image_name to image table

Revision ID: 452f34e8ea3
Revises: 5583c6e70156
Create Date: 2015-04-02 22:07:34.346737

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '452f34e8ea3'
down_revision = '5583c6e70156'


def upgrade():
    op.add_column('image', sa.Column('docker_image_name',
                                     sa.String(length=512)))


def downgrade():
    op.drop_column('image', 'docker_image_name')
