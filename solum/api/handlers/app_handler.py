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

import uuid

from solum.api.handlers import handler
from solum.api.handlers import workflow_handler
from solum.common import exception
from solum.common import keystone_utils
from solum import objects
from solum.openstack.common import log as logging


LOG = logging.getLogger(__name__)


class AppHandler(handler.Handler):
    """Fulfills a request on the app resource."""

    def get(self, id):
        """Return an app."""
        return objects.registry.App.get_by_uuid(self.context, id)

    def patch(self, id, data):
        """Update an app."""
        db_obj = objects.registry.App.get_by_uuid(self.context, id)

        data_dict = data.as_dict(objects.registry.App)
        obj_dict = db_obj.as_dict()

        # Source and workflow are a little tricky to update.
        new_source = obj_dict['source']
        new_source.update(data_dict.get('source', {}))
        data_dict['source'] = new_source

        new_wf = obj_dict['workflow_config']
        new_wf.update(data_dict.get('workflow_config', {}))
        data_dict['workflow_config'] = new_wf

        updated = objects.registry.App.update_and_save(self.context,
                                                       id, data_dict)
        return updated

    def delete(self, id):
        """Delete an existing app."""
        # First delete workflows based on app_id
        objects.registry.Workflow.destroy(id)

        # Now delete the app
        db_obj = objects.registry.App.get_by_uuid(self.context, id)
        db_obj.destroy(self.context)

    def create(self, data):
        """Create a new app."""
        db_obj = objects.registry.App()
        db_obj.id = str(uuid.uuid4())
        db_obj.user_id = self.context.user
        db_obj.project_id = self.context.tenant
        db_obj.deleted = False

        # create a delegation trust_id\token, if required
        db_obj.trust_id = keystone_utils.create_delegation_token(self.context)
        db_obj.trust_user = self.context.user_name

        db_obj.name = data.get('name')
        db_obj.description = data.get('description')
        db_obj.languagepack = data.get('languagepack')
        db_obj.stack_id = data.get('stack_id')
        db_obj.ports = data.get('ports')
        db_obj.source = data.get('source')
        db_obj.workflow_config = data.get('workflow_config')
        db_obj.trigger_uuid = str(uuid.uuid4())
        db_obj.trigger_actions = data.get('trigger_actions')

        db_obj.create(self.context)
        return db_obj

    def trigger_workflow(self, trigger_id, commit_sha='',
                         status_url=None, collab_url=None, workflow=None):
        """Get trigger by trigger id and start git workflow associated."""
        # Note: self.context will be None at this point as this is a
        # non-authenticated request.
        app_obj = objects.registry.App.get_by_trigger_id(None, trigger_id)
        # get the trust context and authenticate it.
        try:
            self.context = keystone_utils.create_delegation_context(
                app_obj, self.context)
            self.context.tenant = app_obj.project_id
            self.context.user = app_obj.user_id
            self.context.user_name = app_obj.trust_user

        except exception.AuthorizationFailure as auth_ex:
            LOG.warn(auth_ex)
            return

        # TODO(devkulkarni): Call repo_utils.verify_artifact
        # as we are calling it in the plan_handler to verify
        # the collaborator
        self._build_artifact(app_obj, commit_sha=commit_sha,
                             status_url=status_url, wf=workflow)

    def _build_artifact(self, app, commit_sha='',
                        status_url=None, wf=None):

        if wf is None:
            wf = ['unittest', 'build', 'deploy']
        wfhand = workflow_handler.WorkflowHandler(self.context)

        wfdata = {
            'app_id': app.id,
            'name': "%s" % app.name,
            'description': '',
            'source': app.source,
            'config': app.workflow_config,
            'actions': wf
            }
        wfhand.create(wfdata, commit_sha=commit_sha, status_url=status_url)

    def get_all(self):
        """Return all apps."""
        all_apps = objects.registry.AppList.get_all(self.context)
        return all_apps
