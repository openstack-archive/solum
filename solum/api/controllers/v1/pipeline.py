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

import pecan
from pecan import rest
import wsme
import wsmeext.pecan as wsme_pecan

from solum.api.controllers.v1.datamodel import pipeline
from solum.api.controllers.v1 import execution
from solum.api.handlers import pipeline_handler
from solum.common import exception
from solum.common import policy
from solum.i18n import _
from solum import objects


class PipelineController(rest.RestController):
    """Manages operations on a single pipeline."""

    executions = execution.ExecutionsController()

    def __init__(self, pipeline_id):
        super(PipelineController, self).__init__()
        self._id = pipeline_id

    @exception.wrap_wsme_pecan_controller_exception
    @wsme_pecan.wsexpose(pipeline.Pipeline)
    def get(self):
        """Return this pipeline."""
        policy.check('show_pipeline',
                     pecan.request.security_context)
        handler = pipeline_handler.PipelineHandler(
            pecan.request.security_context)
        host_url = pecan.request.application_url.rstrip('/')
        return pipeline.Pipeline.from_db_model(handler.get(self._id), host_url)

    @exception.wrap_wsme_pecan_controller_exception
    @wsme_pecan.wsexpose(pipeline.Pipeline, body=pipeline.Pipeline)
    def put(self, data):
        """Modify this pipeline."""
        policy.check('update_pipeline',
                     pecan.request.security_context)
        handler = pipeline_handler.PipelineHandler(
            pecan.request.security_context)
        res = handler.update(self._id,
                             data.as_dict(objects.registry.Pipeline))
        host_url = pecan.request.application_url.rstrip('/')
        return pipeline.Pipeline.from_db_model(res, host_url)

    @exception.wrap_wsme_pecan_controller_exception
    @wsme_pecan.wsexpose(status_code=204)
    def delete(self):
        """Delete this pipeline."""
        policy.check('delete_pipeline',
                     pecan.request.security_context)
        handler = pipeline_handler.PipelineHandler(
            pecan.request.security_context)
        return handler.delete(self._id)


class PipelinesController(rest.RestController):
    """Manages operations on the pipeline collection."""

    @pecan.expose()
    def _lookup(self, pipeline_id, *remainder):
        if remainder and not remainder[-1]:
            remainder = remainder[:-1]
        return PipelineController(pipeline_id), remainder

    @exception.wrap_wsme_pecan_controller_exception
    @wsme_pecan.wsexpose(pipeline.Pipeline,
                         body=pipeline.Pipeline,
                         status_code=201)
    def post(self, data):
        """Create a new pipeline."""
        policy.check('create_pipeline', pecan.request)
        js_data = data.as_dict(objects.registry.Pipeline)
        host_url = pecan.request.application_url.rstrip('/')
        if data.plan_uri is not wsme.Unset:
            plan_uri = data.plan_uri
            if plan_uri.startswith(host_url):
                pl_uuid = plan_uri.split('/')[-1]
                pl = objects.registry.Plan.get_by_uuid(
                    pecan.request.security_context, pl_uuid)
                js_data['plan_id'] = pl.id
            else:
                # TODO(asalkeld) we are not hosting the plan so
                # download the plan and insert it into our db.
                raise exception.BadRequest(reason=_(
                    'The plan was not hosted in solum'))

        if js_data.get('plan_id') is None:
            raise exception.BadRequest(reason=_(
                'The plan was not given or could not be found'))

        handler = pipeline_handler.PipelineHandler(
            pecan.request.security_context)
        return pipeline.Pipeline.from_db_model(
            handler.create(js_data), host_url)

    @exception.wrap_wsme_pecan_controller_exception
    @wsme_pecan.wsexpose([pipeline.Pipeline])
    def get_all(self):
        """Return all pipelines."""
        policy.check('get_pipelines',
                     pecan.request.security_context)
        handler = pipeline_handler.PipelineHandler(
            pecan.request.security_context)
        host_url = pecan.request.application_url.rstrip('/')
        return [pipeline.Pipeline.from_db_model(obj, host_url)
                for obj in handler.get_all()]
