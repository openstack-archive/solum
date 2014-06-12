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
from solum.common import context
from solum.common import exception
from solum.common import solum_keystoneclient
from solum import objects
from solum.openstack.common import log as logging

LOG = logging.getLogger(__name__)
CONF = cfg.CONF


class PipelineHandler(handler.Handler):
    """Fulfills a request on the pipeline resource."""

    def get(self, id):
        """Return an pipeline."""
        return objects.registry.Pipeline.get_by_uuid(self.context, id)

    def _context_from_trust_id(self, trust_id):
        cntx = context.RequestContext(trust_id=trust_id)
        kc = solum_keystoneclient.KeystoneClientV3(cntx)
        return kc.context

    def trigger_workflow(self, trigger_id):
        """Get trigger by trigger id and execute the associated workbook."""
        # Note: self.context will be None at this point as this is a
        # non-authenticated request.
        db_obj = objects.registry.Pipeline.get_by_trigger_id(None,
                                                             trigger_id)
        # get the trust context and authenticate it.
        try:
            self.context = self._context_from_trust_id(db_obj.trust_id)
        except exception.AuthorizationFailure as auth_ex:
            LOG.warn(auth_ex)
            return

        self._execute_workbook(db_obj)

    def _execute_workbook(self, pipeline):
        # TODO(asalkeld) execute the mistral workbook.
        pass

    def update(self, id, data):
        """Modify a resource."""
        db_obj = objects.registry.Pipeline.get_by_uuid(self.context, id)
        db_obj.update(data)
        db_obj.save(self.context)
        return db_obj

    def delete(self, id):
        """Delete a resource."""
        db_obj = objects.registry.Pipeline.get_by_uuid(self.context, id)

        # delete the trust.
        ksc = solum_keystoneclient.KeystoneClientV3(self.context)
        ksc.delete_trust(db_obj.trust_id)
        db_obj.delete(self.context)

    def create(self, data):
        """Create a new resource."""
        db_obj = objects.registry.Pipeline()
        db_obj.update(data)
        db_obj.uuid = str(uuid.uuid4())
        db_obj.user_id = self.context.user
        db_obj.project_id = self.context.tenant
        db_obj.trigger_id = str(uuid.uuid4())

        # create the trust_id and store it.
        ksc = solum_keystoneclient.KeystoneClientV3(self.context)
        trust_context = ksc.create_trust_context()
        db_obj.trust_id = trust_context.trust_id

        db_obj.create(self.context)

        self._execute_workbook(db_obj)

        return db_obj

    def get_all(self):
        """Return all pipelines, based on the query provided."""
        return objects.registry.PipelineList.get_all(self.context)
