# Copyright 2015 - Rackspace US, Inc.
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

from oslo_config import cfg
import pecan
from pecan import rest
import wsmeext.pecan as wsme_pecan

from solum.api.controllers.v1.datamodel import workflow
from solum.api.controllers.v1 import userlog as userlog_controller
from solum.api.handlers import app_handler
from solum.api.handlers import workflow_handler as wf_handler
from solum.common import clients
from solum.common import exception
from solum.common import request

cfg.CONF.import_opt('image_storage', 'solum.worker.config', group='worker')


class WorkflowController(rest.RestController):
    """Manages operations on a single workflow."""

    def __init__(self, app_id, wf_id):
        super(WorkflowController, self).__init__(self)
        self.app_id = app_id
        self.wf_id = wf_id

    @pecan.expose()
    def _lookup(self, primary_key, *remainder):
        if remainder and not remainder[-1]:
            remainder = remainder[:-1]
        if primary_key == 'logs':
            logs = userlog_controller.UserlogsController(self.wf_id)
            return logs, remainder

    @exception.wrap_pecan_controller_exception
    @wsme_pecan.wsexpose(workflow.Workflow)
    def get(self):
        """Return this workflow."""
        request.check_request_for_https()
        handler = wf_handler.WorkflowHandler(pecan.request.security_context)
        wf_model = handler.get(self.wf_id)
        host_url = pecan.request.application_url.rstrip('/')
        wf_model = workflow.Workflow.from_db_model(wf_model, host_url)
        return wf_model


class WorkflowsController(rest.RestController):
    """Manages operations on all of an app's workflows."""

    def __init__(self, app_id):
        super(WorkflowsController, self).__init__(self)
        self.app_id = app_id

    @pecan.expose()
    def _lookup(self, wf_uuid, *remainder):
        if remainder and not remainder[-1]:
            remainder = remainder[:-1]
        return WorkflowController(self.app_id, wf_uuid), remainder

    @exception.wrap_pecan_controller_exception
    @wsme_pecan.wsexpose(workflow.Workflow, body=workflow.Workflow,
                         status_code=200)
    def post(self, data):
        """Create a new workflow."""
        request.check_request_for_https()
        if not data:
            raise exception.BadRequest(reason='No data.')

        ahandler = app_handler.AppHandler(pecan.request.security_context)
        app_model = ahandler.get(self.app_id)

        handler = wf_handler.WorkflowHandler(pecan.request.security_context)

        data.app_id = app_model.id
        data.config = app_model.workflow_config
        data.source = app_model.source

        wf_data = data.as_dict(workflow.Workflow)

        du_id = None
        if data.du_id:
            du_id = data.du_id
            self._verify_du_exists(pecan.request.security_context, du_id)

        host_url = pecan.request.application_url.rstrip('/')
        return workflow.Workflow.from_db_model(handler.create(wf_data,
                                                              commit_sha='',
                                                              status_url='',
                                                              du_id=du_id),
                                               host_url)

    @exception.wrap_pecan_controller_exception
    @wsme_pecan.wsexpose([workflow.Workflow])
    def get_all(self):
        """Return all of one app's workflows, based on the query provided."""
        request.check_request_for_https()
        handler = wf_handler.WorkflowHandler(pecan.request.security_context)
        host_url = pecan.request.application_url.rstrip('/')
        all_wfs = [workflow.Workflow.from_db_model(obj, host_url)
                   for obj in handler.get_all(app_id=self.app_id)]
        return all_wfs

    def _verify_du_exists(self, ctxt, du_id):
        du_image_backend = cfg.CONF.worker.image_storage
        if du_image_backend.lower() == 'glance':
            self._verify_du_image_exists_in_glance(ctxt, du_id)
        elif du_image_backend.lower() == 'swift':
            self._verify_du_image_exists_in_swift(ctxt, du_id)
        else:
            raise exception.BadRequest(message="DU image id not recognized.")
        return

    def _verify_du_image_exists_in_glance(self, ctxt, du_id):
        osc = clients.OpenStackClients(ctxt)
        osc.glance().images.get(du_id)
        return

    def _verify_du_image_exists_in_swift(self, du_id):
        # TODO(devkulkarni): Check if specified du_id exists in swift
        return
