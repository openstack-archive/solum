# Copyright 2013 - Rackspace
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

from oslo.config import cfg
from solum.api.handlers import handler
from solum import objects
from solum.worker import api

# Register options for the service
API_SERVICE_OPTS = [
    cfg.StrOpt('image_format',
               default='qcow2',
               help='The format of the image to output'),
]

CONF = cfg.CONF
opt_group = cfg.OptGroup(name='api',
                         title='Options for the solum-api service')
CONF.register_group(opt_group)
CONF.register_opts(API_SERVICE_OPTS, opt_group)


class AssemblyHandler(handler.Handler):
    """Fulfills a request on the assembly resource."""

    def get(self, id):
        """Return an assembly."""
        return objects.registry.Assembly.get_by_uuid(self.context, id)

    def trigger_workflow(self, trigger_id):
        """Get trigger by trigger id and start git worflow associated."""
        # Note: self.context will be None at this point as this is a
        # non-authenticated request.
        db_obj = objects.registry.Assembly.get_by_trigger_id(self.context,
                                                             trigger_id)
        plan_obj = objects.registry.Plan.get_by_id(self.context,
                                                   db_obj.plan_id)
        artifacts = plan_obj.raw_content.get('artifacts', [])
        for arti in artifacts:
            self._build_artifact(db_obj, plan_obj, arti)

    def update(self, id, data):
        """Modify a resource."""
        db_obj = objects.registry.Assembly.get_by_uuid(self.context, id)
        db_obj.update(data)
        db_obj.save(self.context)
        return db_obj

    def delete(self, id):
        """Delete a resource."""
        db_obj = objects.registry.Assembly.get_by_uuid(self.context, id)
        db_obj.destroy(self.context)

    def create(self, data):
        """Create a new resource."""
        db_obj = objects.registry.Assembly()
        db_obj.update(data)
        db_obj.uuid = str(uuid.uuid4())
        db_obj.user_id = self.context.user
        db_obj.project_id = self.context.tenant
        db_obj.trigger_id = str(uuid.uuid4())
        db_obj.create(self.context)
        plan_obj = objects.registry.Plan.get_by_id(self.context,
                                                   db_obj.plan_id)
        artifacts = plan_obj.raw_content.get('artifacts', [])
        for arti in artifacts:
            self._build_artifact(db_obj, plan_obj, arti)
        return db_obj

    def _build_artifact(self, assem, plan, artifact):
        # This is a tempory hack so we don't need the build client
        # in the requirments.
        image = objects.registry.Image()
        image.name = artifact['name']
        image.source_uri = artifact['content']['href']
        image.base_image_id = artifact.get('language_pack', 'auto')
        image.source_format = 'heroku'
        image.image_format = CONF.api.image_format
        image.uuid = str(uuid.uuid4())
        image.user_id = self.context.user
        image.project_id = self.context.tenant
        image.state = api.PENDING
        image.create(self.context)

        api.API(context=self.context).build(
            build_id=image.id,
            source_uri=image.source_uri,
            name=image.name,
            base_image_id=image.base_image_id,
            source_format=image.source_format,
            image_format=image.image_format,
            assembly_id=assem.id)

    def get_all(self):
        """Return all assemblies, based on the query provided."""
        return objects.registry.AssemblyList.get_all(self.context)
