# Copyright 2014 - Rackspace
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import sqlalchemy as sa

from solum import objects
from solum.objects import component as abstract
from solum.objects.sqlalchemy import models as sql

from oslo_utils import uuidutils


class Component(sql.Base, abstract.Component):
    """Represent an component in sqlalchemy."""

    __tablename__ = 'component'
    __resource__ = 'components'
    __table_args__ = sql.table_args()

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    uuid = sa.Column(sa.String(36))
    project_id = sa.Column(sa.String(36))
    user_id = sa.Column(sa.String(36))
    name = sa.Column(sa.String(100))
    component_type = sa.Column(sa.String(100))
    description = sa.Column(sa.String(255))
    tags = sa.Column(sa.Text)
    assembly_id = sa.Column(sa.Integer, sa.ForeignKey('assembly.id'))
    parent_component_id = sa.Column(sa.Integer, sa.ForeignKey('component.id'))
    resource_uri = sa.Column(sa.String(1024))
    heat_stack_id = sa.Column(sa.String(36))

    @property
    def assembly_uuid(self):
        if self.assembly_id is None:
            return None
        return objects.registry.Assembly.get_by_id(None, self.assembly_id).uuid

    @assembly_uuid.setter
    def assembly_uuid(self, assembly_uuid):
        assembly = objects.registry.Assembly.get_by_uuid(None, assembly_uuid)
        self.assembly_id = assembly.id

    @property
    def _extra_keys(self):
        return ['assembly_uuid']

    @staticmethod
    def assign_and_create(ctxt, assem, name, type, description, resource_uri,
                          stack_id):
        """Helper function to make creating components easier."""
        comp = objects.registry.Component()
        comp.uuid = uuidutils.generate_uuid()
        comp.name = name
        comp.component_type = type
        comp.description = description
        comp.assembly_id = assem.id
        comp.user_id = ctxt.user
        comp.project_id = ctxt.project_id
        comp.resource_uri = resource_uri
        comp.heat_stack_id = stack_id
        comp.create(ctxt)
        return comp


class ComponentList(abstract.ComponentList):
    """Represent a list of components in sqlalchemy."""

    @classmethod
    def get_all(cls, context):
        return ComponentList(sql.model_query(context, Component))
