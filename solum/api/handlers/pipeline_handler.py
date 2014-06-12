# Copyright 2014 - Rackspace Hosting
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
from solum.openstack.common import log as logging

LOG = logging.getLogger(__name__)
CONF = cfg.CONF


class PipelineHandler(handler.Handler):
    """Fulfills a request on the pipeline resource."""

    def get(self, id):
        """Return an pipeline."""
        return objects.registry.Pipeline.get_by_uuid(self.context, id)

    def update(self, id, data):
        """Modify a resource."""
        db_obj = objects.registry.Pipeline.get_by_uuid(self.context, id)
        db_obj.update(data)
        db_obj.save(self.context)
        return db_obj

    def delete(self, id):
        """Delete a resource."""
        db_obj = objects.registry.Pipeline.get_by_uuid(self.context, id)
        db_obj.delete(self.context)

    def create(self, data):
        """Create a new resource."""
        db_obj = objects.registry.Pipeline()
        db_obj.update(data)
        db_obj.uuid = str(uuid.uuid4())
        db_obj.user_id = self.context.user
        db_obj.project_id = self.context.tenant
        db_obj.trigger_id = str(uuid.uuid4())
        db_obj.create(self.context)
        return db_obj

    def get_all(self):
        """Return all pipelines, based on the query provided."""
        return objects.registry.PipelineList.get_all(self.context)
