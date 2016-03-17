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

"""Create initial Solum DB schema

Revision ID: 498adc6185ae
Revises: None
Create Date: 2014-02-03 15:51:20.819539

"""
from alembic import op
import sqlalchemy as sa

from solum.objects.sqlalchemy import models

from oslo_utils import timeutils

# revision identifiers, used by Alembic.
revision = '498adc6185ae'
down_revision = None


def upgrade():
    op.create_table(
        'sensor',
        sa.Column('id', sa.Integer, primary_key=True, nullable=False),
        sa.Column('uuid', sa.String(length=36), nullable=False),
        sa.Column('created_at', sa.DateTime, default=timeutils.utcnow),
        sa.Column('updated_at', sa.DateTime, onupdate=timeutils.utcnow),
        sa.Column('project_id', sa.String(length=36)),
        sa.Column('user_id', sa.String(length=36)),
        sa.Column('name', sa.String(255)),
        sa.Column('sensor_type', sa.String(255)),
        sa.Column('value', sa.String(255)),
        sa.Column('timestamp', sa.DateTime),
        sa.Column('description', sa.String(255)),
        sa.Column('documentation', sa.String(255)),
        sa.Column('target_resource', sa.String(255)),
    )

    op.create_table(
        'operation',
        sa.Column('id', sa.Integer, primary_key=True, nullable=False),
        sa.Column('uuid', sa.String(length=36), nullable=False),
        sa.Column('created_at', sa.DateTime, default=timeutils.utcnow),
        sa.Column('updated_at', sa.DateTime, onupdate=timeutils.utcnow),
        sa.Column('name', sa.String(100)),
        sa.Column('description', sa.String(255)),
        sa.Column('project_id', sa.String(36)),
        sa.Column('user_id', sa.String(36)),
        sa.Column('tags', sa.Text),
        sa.Column('documentation', sa.Text),
        sa.Column('target_resource', sa.Text)
    )

    op.create_table(
        'image',
        sa.Column('id', sa.Integer, primary_key=True, nullable=False),
        sa.Column('uuid', sa.String(36), nullable=False),
        sa.Column('created_at', sa.DateTime, default=timeutils.utcnow),
        sa.Column('updated_at', sa.DateTime, onupdate=timeutils.utcnow),
        sa.Column('name', sa.String(100)),
        sa.Column('description', sa.String(255)),
        sa.Column('source_uri', sa.String(1024)),
        sa.Column('project_id', sa.String(36)),
        sa.Column('user_id', sa.String(36)),
        sa.Column('tags', sa.Text),
        sa.Column('state', sa.String(12)),
        sa.Column('base_image_id', sa.String(length=36)),
        sa.Column('created_image_id', sa.String(length=36)),
        sa.Column('image_format', sa.String(length=12)),
        sa.Column('source_format', sa.String(length=36)),
    )

    op.create_table(
        'extension',
        sa.Column('id', sa.Integer, primary_key=True, nullable=False),
        sa.Column('uuid', sa.String(length=36), nullable=False),
        sa.Column('created_at', sa.DateTime, default=timeutils.utcnow),
        sa.Column('updated_at', sa.DateTime, onupdate=timeutils.utcnow),
        sa.Column('project_id', sa.String(36)),
        sa.Column('user_id', sa.String(36)),
        sa.Column('description', sa.String(255)),
        sa.Column('name', sa.String(100)),
        sa.Column('version', sa.String(16)),
        sa.Column('documentation', sa.String(255)),
        # NOTE(stannie): tags will be added in a dedicated table
    )

    op.create_table(
        'plan',
        sa.Column('id', sa.Integer, primary_key=True, nullable=False),
        sa.Column('uuid', sa.String(length=36), nullable=False),
        sa.Column('created_at', sa.DateTime, default=timeutils.utcnow),
        sa.Column('updated_at', sa.DateTime, onupdate=timeutils.utcnow),
        sa.Column('project_id', sa.String(length=36)),
        sa.Column('user_id', sa.String(length=36)),
        sa.Column('raw_content', models.YAMLEncodedDict(2048)),
        sa.Column('description', sa.String(length=255)),
        sa.Column('name', sa.String(255)),
        sa.Column('deploy_keys_uri', sa.String(length=1024)),
    )

    op.create_table(
        'assembly',
        sa.Column('id', sa.Integer, primary_key=True, nullable=False),
        sa.Column('uuid', sa.String(length=36), nullable=False),
        sa.Column('created_at', sa.DateTime, default=timeutils.utcnow),
        sa.Column('updated_at', sa.DateTime, onupdate=timeutils.utcnow),
        sa.Column('name', sa.String(100)),
        sa.Column('description', sa.String(255)),
        sa.Column('project_id', sa.String(36)),
        sa.Column('user_id', sa.String(36)),
        sa.Column('tags', sa.Text),
        sa.Column('plan_id', sa.Integer, sa.ForeignKey('plan.id'),
                  nullable=False),
        sa.Column('status', sa.String(length=36)),
        sa.Column('trigger_id', sa.String(length=36)),
        sa.Column('trust_id', sa.String(length=255)),
        sa.Column('application_uri', sa.String(length=1024)),
    )

    op.create_table(
        'pipeline',
        sa.Column('id', sa.Integer, primary_key=True, nullable=False),
        sa.Column('uuid', sa.String(length=36), nullable=False),
        sa.Column('created_at', sa.DateTime, default=timeutils.utcnow),
        sa.Column('updated_at', sa.DateTime, onupdate=timeutils.utcnow),
        sa.Column('name', sa.String(100)),
        sa.Column('description', sa.String(255)),
        sa.Column('project_id', sa.String(36)),
        sa.Column('user_id', sa.String(36)),
        sa.Column('tags', sa.Text),
        sa.Column('plan_id', sa.Integer, sa.ForeignKey('plan.id'),
                  nullable=False),
        sa.Column('workbook_name', sa.String(length=255)),
        sa.Column('trigger_id', sa.String(length=36)),
        sa.Column('trust_id', sa.String(length=255)),
    )

    op.create_table(
        'execution',
        sa.Column('id', sa.Integer, primary_key=True, nullable=False),
        sa.Column('uuid', sa.String(length=36), nullable=False),
        sa.Column('pipeline_id', sa.Integer, sa.ForeignKey('pipeline.id')),
        sa.Column('created_at', sa.DateTime, default=timeutils.utcnow),
        sa.Column('updated_at', sa.DateTime, onupdate=timeutils.utcnow),
    )

    op.create_table(
        'infrastructure_stack',
        sa.Column('id', sa.Integer, primary_key=True, nullable=False),
        sa.Column('uuid', sa.String(length=36), nullable=False),
        sa.Column('created_at', sa.DateTime, default=timeutils.utcnow),
        sa.Column('updated_at', sa.DateTime, onupdate=timeutils.utcnow),
        sa.Column('name', sa.String(100)),
        sa.Column('description', sa.String(255)),
        sa.Column('project_id', sa.String(36)),
        sa.Column('user_id', sa.String(36)),
        sa.Column('tags', sa.Text),
        sa.Column('image_id', sa.String(36), nullable=False),
        sa.Column('heat_stack_id', sa.String(36)),
    )

    op.create_table(
        'component',
        sa.Column('id', sa.Integer, primary_key=True, nullable=False),
        sa.Column('uuid', sa.String(length=36), nullable=False),
        sa.Column('created_at', sa.DateTime, default=timeutils.utcnow),
        sa.Column('updated_at', sa.DateTime, onupdate=timeutils.utcnow),
        sa.Column('name', sa.String(100)),
        sa.Column('component_type', sa.String(100)),
        sa.Column('description', sa.String(255)),
        sa.Column('project_id', sa.String(36)),
        sa.Column('user_id', sa.String(36)),
        sa.Column('tags', sa.Text),
        sa.Column('assembly_id', sa.Integer, sa.ForeignKey('assembly.id')),
        sa.Column('parent_component_id', sa.Integer,
                  sa.ForeignKey('component.id')),
        sa.Column('resource_uri', sa.String(length=1024)),
        sa.Column('heat_stack_id', sa.String(36)),
    )

    op.create_table(
        'service',
        sa.Column('id', sa.Integer, primary_key=True, nullable=False),
        sa.Column('uuid', sa.String(36), nullable=False),
        sa.Column('created_at', sa.DateTime, default=timeutils.utcnow),
        sa.Column('updated_at', sa.DateTime, onupdate=timeutils.utcnow),
        sa.Column('name', sa.String(100)),
        sa.Column('description', sa.String(255)),
        sa.Column('project_id', sa.String(36)),
        sa.Column('user_id', sa.String(36)),
        sa.Column('service_type', sa.String(100)),
        sa.Column('read_only', sa.Integer, default=0),
        sa.Column('tags', sa.Text),
    )


def downgrade():
    op.drop_table('service')
    op.drop_table('component')
    op.drop_table('assembly')
    op.drop_table('plan')
    op.drop_table('extension')
    op.drop_table('image')
    op.drop_table('operation')
    op.drop_table('sensor')
