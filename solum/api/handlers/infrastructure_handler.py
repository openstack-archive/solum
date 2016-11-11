# Copyright 2014 - Numergy
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

from oslo_utils import uuidutils

from solum.api.handlers import handler
from solum.common import catalog
from solum.common import clients
from solum import objects


class InfrastructureStackHandler(handler.Handler):
    """Fulfills a request on the infrastructure stack resource."""

    def get(self, id):
        """Return a stack."""
        return objects.registry.InfrastructureStack.get_by_uuid(
            self.context, id)

    def update(self, id, data):
        """Modify a stack."""
        updated = objects.registry.InfrastructureStack.update_and_save(
            self.context, id, data)
        return updated

    def delete(self, id):
        """Delete a stack."""
        db_obj = objects.registry.InfrastructureStack.get_by_uuid(
            self.context, id)
        db_obj.destroy(self.context)

    def create(self, data):
        """Create a new stack.

        Create a new infrastructure stack by using Heat. Note that a zaqar
        queue is created and will be consumed by solum-infra-guestagent.
        """
        db_obj = objects.registry.InfrastructureStack()
        db_obj.update(data)
        db_obj.uuid = uuidutils.generate_uuid()
        db_obj.user_id = self.context.user
        db_obj.project_id = self.context.tenant

        self._create_zaqar_queue(db_obj.uuid)
        db_obj.heat_stack_id = self._deploy_infra(data.get('image_id'))

        db_obj.create(self.context)
        return db_obj

    def _create_zaqar_queue(self, queue_name):
        osc = clients.OpenStackClients(self.context)
        osc.zaqar().queue(queue_name)

    def _deploy_infra(self, image_id):
        osc = clients.OpenStackClients(self.context)

        parameters = {'image': image_id}

        template = catalog.get('templates', 'infra')

        created_stack = osc.heat().stacks.create(stack_name='infra',
                                                 template=template,
                                                 parameters=parameters)
        return created_stack['stack']['id']

    def get_all(self):
        """Return all stacks, based on the query provided."""
        return objects.registry.InfrastructureStackList.get_all(self.context)
