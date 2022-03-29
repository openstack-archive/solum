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
import json

from oslo_config import cfg
from oslo_utils import uuidutils

from solum.api.handlers import handler
from solum.common import exception
from solum.common import repo_utils
from solum import objects
from solum.objects import image
from solum.objects.sqlalchemy import workflow
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
    cfg.IntOpt('max_instances_per_app',
               default=100,
               help='Application scale limit'),
]


def list_opts():
    yield 'api', API_SERVICE_OPTS


CONF = cfg.CONF
CONF.register_opts(API_SERVICE_OPTS, group='api')

IMAGE_STATES = image.States


class WorkflowHandler(handler.Handler):
    """Fulfills a request on the workflow resource."""

    def _update_app_scale_config(self, app, data):

        scale_config = dict()
        target = data.get('scale_target', '1')
        try:
            target = int(target)
        except ValueError:
            msg = "Must provide integer value for scale target."
            raise exception.BadRequest(reason=msg)

        if target <= 0:
            msg = "Scale target must be greater than zero."
            raise exception.BadRequest(reason=msg)

        if target > cfg.CONF.api.max_instances_per_app:
            msg = "Target scale '%s' exceeds maximum scale limit '%s'." % (
                target, cfg.CONF.api.max_instances_per_app)
            raise exception.ResourceLimitExceeded(reason=msg)

        current_config = app.scale_config

        if current_config:
            current_config[app.name]['target'] = str(target)
            scale_config['scale_config'] = current_config
        else:
            config_data = dict()
            config_data['target'] = str(target)
            app_scale_config = dict()
            app_scale_config[app.name] = config_data
            scale_config = dict()
            scale_config['scale_config'] = app_scale_config

        objects.registry.App.update_and_save(self.context, app.id,
                                             scale_config)

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

    def create(self, data, commit_sha, status_url, du_id):
        """Create a new workflow."""

        db_obj = objects.registry.Workflow()
        db_obj.id = uuidutils.generate_uuid()
        db_obj.user_id = self.context.user
        db_obj.project_id = self.context.project_id
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

        if str(app_obj.languagepack).lower() == 'false' and not du_id:
            msg = ("App {app} registered without a languagepack and no "
                   "du id specified. Either register the app with"
                   " a languagepack, or if there is already a pre"
                   "built du for the app, specify its id with --du-id"
                   " command line flag.")
            msg = msg.format(app=app_obj.name)
            raise exception.BadRequest(reason=msg)

        self._update_app_scale_config(app_obj, data)

        plan, assem = PlanAssemblyAdapter(self.context,
                                          db_obj,
                                          app_obj).create_dummies()

        db_obj.assembly = assem.id

        workflow.Workflow.insert(self.context, db_obj)

        self._execute_workflow_actions(db_obj, app_obj, assem,
                                       commit_sha=commit_sha,
                                       status_url=status_url,
                                       du_id=du_id)

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
                                  commit_sha='', status_url=None,
                                  du_id=None):
        image = objects.registry.Image()

        image.name = app_obj.name
        image.source_uri = wf_obj.source['repository']
        image.base_image_id = app_obj.languagepack
        image.image_format = CONF.api.image_format
        image.uuid = uuidutils.generate_uuid()
        image.user_id = self.context.user
        image.project_id = self.context.project_id
        image.status = IMAGE_STATES.QUEUED
        image.create(self.context)
        test_cmd = wf_obj.config['test_cmd']
        run_cmd = wf_obj.config['run_cmd']

        ports = app_obj.ports

        app_raw_content = json.loads(app_obj.raw_content)
        if ('repo_token' in app_raw_content):
            repo_token = app_raw_content['repo_token']
        else:
            repo_token = ''

        if ('private' in wf_obj.source.keys()):
            private = wf_obj.source['private']
        else:
            private = False

        if ('private_ssh_key' in wf_obj.source.keys()):
            private_ssh_key = wf_obj.source['private_ssh_key']
        else:
            private_ssh_key = ''

        # TODO(devkulkarni): Check whether we need image.source_format
        image.source_format = 'solum'

        git_info = {
            'source_url': image.source_uri,
            'commit_sha': commit_sha,
            'repo_token': repo_token,
            'status_url': status_url,
            'private': private,
            'private_ssh_key': private_ssh_key
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
            run_cmd=run_cmd,
            du_id=du_id)


class PlanAssemblyAdapter(object):
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
        # Create only one plan
        try:
            plan = objects.registry.Plan.get_by_uuid(self.context,
                                                     self.app_obj.id)
        except exception.ResourceNotFound:
            plan = objects.registry.Plan()
            plan.uuid = self.app_obj.id
            plan.user_id = self.context.user
            plan.project_id = self.context.project_id
            plan.name = self.app_obj.name
            plan.create(self.context)

        assembly = objects.registry.Assembly()
        assembly.plan_id = plan.id
        assembly.user_id = self.context.user
        assembly.project_id = self.context.project_id
        assembly.name = self.app_obj.name
        assembly.uuid = uuidutils.generate_uuid()

        assembly.workflow = self.wf_obj.actions

        assembly.create(self.context)

        return plan, assembly
