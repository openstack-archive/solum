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

import json

from mistralclient.api import base
from oslo_config import cfg
from oslo_log import log as logging
from oslo_utils import uuidutils

from solum.api.handlers import handler
from solum.common import catalog
from solum.common import clients
from solum.common import context
from solum.common import exception
from solum.common import heat_utils
from solum.common import yamlutils
from solum import objects

LOG = logging.getLogger(__name__)
CONF = cfg.CONF


class PipelineHandler(handler.Handler):
    """Fulfills a request on the pipeline resource."""
    def __init__(self, context):
        super(PipelineHandler, self).__init__(context)
        self._clients = None
        if context is not None:
            self._clients = clients.OpenStackClients(context)

    def get(self, id):
        """Return an pipeline."""
        return objects.registry.Pipeline.get_by_uuid(self.context, id)

    def _context_from_trust_id(self, trust_id):
        cntx = context.RequestContext(trust_id=trust_id)
        self._clients = clients.OpenStackClients(cntx)
        return self._clients.keystone().context

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
            LOG.warning(auth_ex)
            return

        self._execute_workbook(db_obj)

    def _get_context_from_last_execution(self, pipeline):

        last_execution = pipeline.last_execution()
        if last_execution is None:
            return

        osc = self._clients
        try:
            execution = osc.mistral().executions.get(
                pipeline.workbook_name, last_execution.uuid)
            execution_ctx = json.loads(execution.context)
            str_definition = osc.mistral().workbooks.get_definition(
                pipeline.workbook_name)
            definition = yamlutils.load(str_definition)
        except base.APIException:
            LOG.debug('Could not get last_execution(%s)' %
                      last_execution, exc_info=True)
            return

        tasks = definition['Workflow'].get('tasks', {})
        inputs = set()
        outputs = set()
        for act in tasks:
            inputs |= set(tasks[act].get('parameters', {}).keys())
            outputs |= set(tasks[act].get('publish', {}).keys())
        inputs -= outputs
        return dict((key, execution_ctx.get(key)) for key in inputs)

    def _build_execution_context(self, pipeline):
        # try and read the context from the previous execution
        ctx = self._get_context_from_last_execution(pipeline)
        if ctx is not None:
            return ctx

        ctx = {}
        # service urls.
        kc = self._clients.keystone()
        ctx['heat_service_url'] = kc.client.service_catalog.url_for(
            service_type='orchestration',
            interface='publicURL')
        ctx['build_service_url'] = kc.client.service_catalog.url_for(
            service_type='image_builder',
            interface='publicURL')

        # extract context from the plan
        # TODO(asalkeld) this should be versioned.
        plan_obj = objects.registry.Plan.get_by_id(self.context,
                                                   pipeline.plan_id)
        ctx['name'] = plan_obj.name

        artifacts = plan_obj.raw_content.get('artifacts', [])
        for arti in artifacts:
            ctx['source_uri'] = arti['content']['href']
            ctx['base_image_id'] = arti.get('language_pack', 'auto')
            ctx['source_format'] = arti.get('artifact_type', 'heroku')
            ctx['image_format'] = arti.get('image_format',
                                           CONF.api.image_format)

        ctx['template'] = catalog.get('templates', 'basic')
        # TODO(asalkeld) add support to the plan to pass heat parameters.
        ctx['parameters'] = {'app_name': pipeline.name}
        ctx['parameters'].update(
            heat_utils.get_network_parameters(self._clients))
        ctx['stack_id'] = self._create_empty_stack(pipeline)
        ctx['stack_name'] = pipeline.name

        # TODO(asalkeld) integrate the Environment into the context.
        return ctx

    def _create_empty_stack(self, pipeline):
        osc = self._clients
        template = catalog.get('templates', 'empty')
        created_stack = osc.heat().stacks.create(stack_name=pipeline.name,
                                                 template=template)
        return created_stack['stack']['id']

    def _delete_stack(self, pipeline):
        execution_ctx = self._get_context_from_last_execution(pipeline)
        if execution_ctx is not None and 'stack_id' in execution_ctx:
            osc = self._clients
            osc.heat().stacks.delete(stack_id=execution_ctx['stack_id'])

    def _execute_workbook(self, pipeline):
        execution_ctx = self._build_execution_context(pipeline)

        osc = self._clients
        resp = osc.mistral().executions.create(pipeline.workbook_name,
                                               'start',
                                               execution_ctx)
        ex_obj = objects.registry.Execution()
        ex_obj.uuid = resp.id
        ex_obj.pipeline_id = pipeline.id
        ex_obj.create(self.context)

    def _ensure_workbook(self, pipeline):
        osc = clients.OpenStackClients(self.context)
        try:
            osc.mistral().workbooks.get(pipeline.workbook_name)
        except Exception as excp:
            if 'Workbook not found' in str(excp):
                definition = catalog.get('workbooks', pipeline.workbook_name)
                # create the workbook for the user.
                osc.mistral().workbooks.create(
                    pipeline.workbook_name,
                    'solum generated workbook',
                    ['solum', 'builtin'])
                osc.mistral().workbooks.upload_definition(
                    pipeline.workbook_name,
                    definition)
            else:
                raise

    def update(self, id, data):
        """Modify a resource."""
        updated = objects.registry.Pipeline.update_and_save(self.context,
                                                            id, data)
        return updated

    def delete(self, id):
        """Delete a resource."""
        db_obj = objects.registry.Pipeline.get_by_uuid(self.context, id)

        self._delete_stack(db_obj)

        # delete the trust.
        self._clients.keystone().delete_trust(db_obj.trust_id)
        db_obj.destroy(self.context)

    def create(self, data):
        """Create a new resource."""
        db_obj = objects.registry.Pipeline()
        db_obj.update(data)
        db_obj.uuid = uuidutils.generate_uuid()
        db_obj.user_id = self.context.user
        db_obj.project_id = self.context.tenant
        db_obj.trigger_id = uuidutils.generate_uuid()

        # create the trust_id and store it.
        trust_context = self._clients.keystone().create_trust_context()
        db_obj.trust_id = trust_context.trust_id
        db_obj.create(self.context)

        self._ensure_workbook(db_obj)
        self._execute_workbook(db_obj)

        return db_obj

    def get_all(self):
        """Return all pipelines, based on the query provided."""
        return objects.registry.PipelineList.get_all(self.context)
