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

"""empty message

Revision ID: e5f2e8af3b8
Revises: 112cfe038dd3
Create Date: 2015-09-23 18:49:34.292533

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = 'e5f2e8af3b8'
down_revision = '112cfe038dd3'


def upgrade():
    op.create_unique_constraint("app_id_wf_id", "workflow",
                                ['app_id', 'wf_id'])


def downgrade():
    op.drop_unique_constraint("app_id_wf_id", "workflow")
