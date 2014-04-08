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

"""drop service from language_pack

Revision ID: 498adc6185ae
Revises: 4ee48e775ad7
Create Date: 2014-04-02 14:10:32.531136

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '498adc6185ae'
down_revision = '4ee48e775ad7'


def upgrade():
    op.drop_constraint('language_pack_ibfk_1', 'language_pack',
                       type_='foreignkey')
    op.drop_column('language_pack', 'service_id')


def downgrade():
    op.add_column('language_pack', sa.Column('service_id',
                                             sa.Integer,
                                             sa.ForeignKey('service.id'),
                                             nullable=False))
