# Copyright 2015 Rackspace Hosting
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

import datetime
import uuid

from oslo_config import cfg

from solum.api.handlers import handler
from solum.common import repo_utils
from solum import objects
from solum.objects import image
from solum.objects.sqlalchemy import workflow
from solum.openstack.common import log as logging
from solum.worker import api as worker_api

API_SERVICE_OPTS = [
    cfg.StrOpt('image_format',
               default='qcow2',
               help='The format of the image to output'),
    cfg.StrOpt('source_format',
               default='heroku',
               help='The format of source repository'),
    cfg.StrOpt('rebuild_phrase',
               default='solum retry tests',
               help='Comment phrase to trigger rebuilding'),
]

LOG = logging.getLogger(__name__)
CONF = cfg.CONF
CONF.register_opts(API_SERVICE_OPTS, group='api')

IMAGE_STATES = image.States

LOG = logging.getLogger(__name__)


class WorkflowHandler(handler.Handler):
    """Fulfills a request on the workflow resource."""

    def get(self, id):
        """Return a workflow."""
        wf = objects.registry.Workflow.get_by_uuid(self.context, id)

        # Set wf status from that of the corresponding assembly's status
        assembly = objects.registry.Assembly.get_by_id(self.context,
                                                       wf.assembly)
        wf.status = assembly.status
        return wf

    def delete(self, id):
        """Delete an existing workflow."""
        db_obj = objects.registry.Workflow.get_by_uuid(self.context, id)
        db_obj.destroy(self.context)

    def create(self, data, commit_sha, status_url):
        """Create a new workflow."""
        db_obj = objects.registry.Workflow()
        db_obj.id = str(uuid.uuid4())
        db_obj.user_id = self.context.user
        db_obj.project_id = self.context.tenant
        db_obj.deleted = False

        db_obj.app_id = data['app_id']
        db_obj.source = data['source']
        db_obj.config = data['config']
        db_obj.actions = data['actions']

        now = datetime.datetime.utcnow()
        db_obj.created_at = now
        db_obj.updated_at = now

        app_obj = objects.registry.App.get_by_id(self.context,
                                                 db_obj.app_id)

        plan, assem = PlanAssemblyAdapter(self.context,
                                          db_obj,
                                          app_obj).create_dummies()

        db_obj.assembly = assem.id

        workflow.Workflow.insert(self.context, db_obj)

        self._execute_workflow_actions(db_obj, app_obj, assem,
                                       commit_sha=app_obj.source['revision'])

        # TODO(devkulkarni): Update status of actions

        return db_obj

    def get_all_by_id(self, resource_uuid):
        return objects.registry.UserlogList.get_all_by_id(
            self.context, resource_uuid=resource_uuid)

    def get_all(self, app_id=None):
        """Return all of an app's workflows."""
        return objects.registry.WorkflowList.get_all(self.context,
                                                     app_id=app_id)

    def _execute_workflow_actions(self, wf_obj, app_obj, assem,
                                  verb='launch_workflow',
                                  commit_sha='', status_url=None):
        image = objects.registry.Image()

        image.name = app_obj.name
        image.source_uri = wf_obj.source['repository']
        image.base_image_id = app_obj.languagepack
        image.image_format = CONF.api.image_format
        image.uuid = str(uuid.uuid4())
        image.user_id = self.context.user
        image.project_id = self.context.tenant
        image.status = IMAGE_STATES.QUEUED
        image.create(self.context)
        test_cmd = wf_obj.config['test_cmd']
        run_cmd = wf_obj.config['run_cmd']

        ports = app_obj.ports

        # TODO(devkulkarni): Parse repo token from app description
        repo_token = ''

        # TODO(devkulkarni): Check whether we need image.source_format
        image.source_format = 'solum'

        git_info = {
            'source_url': image.source_uri,
            'commit_sha': commit_sha,
            'repo_token': repo_token,
            'status_url': status_url
        }

        if test_cmd:
            repo_utils.send_status(0, status_url, repo_token, pending=True)

        worker_api.API(context=self.context).build_app(
            verb=verb,
            build_id=image.id,
            git_info=git_info,
            ports=ports,
            name=image.name,
            base_image_id=image.base_image_id,
            source_format=image.source_format,
            image_format=image.image_format,
            assembly_id=assem.id,
            workflow=assem.workflow,
            test_cmd=test_cmd,
            run_cmd=run_cmd)


class PlanAssemblyAdapter():
    """Plan and assembly adapter."""
    # Adapter that we use to create assembly and plan
    # objects. This is intended to smooth the transition
    # to the new app and workflow models without causing
    # backwards breaking changes.

    # 1) We need to create Assembly object in our database.
    # This is because,
    # solum/worker/handlers/shell.py and
    # solum/deployer/handlers/heat.py
    # heavily reference 'assembly' (and its attributes)

    # 2) We need to create Plan object because Assembly
    # has a foreign key reference to plan object
    def __init__(self, context, wf_obj, app_obj):
        self.context = context
        self.wf_obj = wf_obj
        self.app_obj = app_obj

    def create_dummies(self):
        plan = objects.registry.Plan()
        plan.uuid = str(uuid.uuid4())
        plan.user_id = self.context.user
        plan.project_id = self.context.tenant
        plan.name = self.app_obj.name
        plan.create(self.context)

        assembly = objects.registry.Assembly()
        assembly.plan_id = plan.id
        assembly.user_id = self.context.user
        assembly.project_id = self.context.tenant
        assembly.name = self.app_obj.name
        assembly.uuid = str(uuid.uuid4())

        assembly.workflow = self.wf_obj.actions

        assembly.create(self.context)

        return plan, assembly