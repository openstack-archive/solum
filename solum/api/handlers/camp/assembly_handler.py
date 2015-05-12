# -*- coding: utf-8 -*-
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

import uuid

from solum.api.handlers import assembly_handler as solum_assem_handler
from solum.common import clients
from solum import objects


class AssemblyHandler(solum_assem_handler.AssemblyHandler):
    def create_from_plan(self, plan_obj):
        """Create an application using a plan resource as a template."""
        db_obj = objects.registry.Assembly()
        db_obj.uuid = str(uuid.uuid4())
        db_obj.user_id = self.context.user
        db_obj.project_id = self.context.tenant
        db_obj.trigger_id = str(uuid.uuid4())
        db_obj.username = self.context.user_name

        # create the trust_id and store it.
        ksc = clients.OpenStackClients(self.context).keystone()
        trust_context = ksc.create_trust_context()
        db_obj.trust_id = trust_context.trust_id

        # use the plan name as the name of this application
        db_obj.name = plan_obj.name + "_application"
        db_obj.plan_id = plan_obj.id
        db_obj.plan_uuid = plan_obj.uuid

        db_obj.status = solum_assem_handler.ASSEMBLY_STATES.QUEUED
        db_obj.create(self.context)
        artifacts = plan_obj.raw_content.get('artifacts', [])

        # build each artifact in the plan
        for arti in artifacts:
            self._build_artifact(assem=db_obj, artifact=arti)

        return db_obj
