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

"""update component foreign keys

Revision ID: 18b94e085cf9
Revises: 12d90235e174
Create Date: 2014-03-10 18:04:58.733470

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = '18b94e085cf9'
down_revision = '12d90235e174'


def upgrade():
    op.create_foreign_key('fk_component_assembly', 'component',
                          'assembly', ['assembly_id'], ['id'])
    op.create_foreign_key('fk_parent_component', 'component',
                          'component', ['parent_component_id'], ['id'])


def downgrade():
    op.drop_constraint('fk_component_assembly', 'component',
                       type_='foreignkey')
    op.drop_constraint('fk_parent_component', 'component', type_='foreignkey')
