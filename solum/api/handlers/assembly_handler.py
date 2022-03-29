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

from oslo_config import cfg
from oslo_log import log as logging
from oslo_utils import uuidutils

from solum.api.handlers import handler
from solum.common import exception
from solum.common import keystone_utils
from solum.common import repo_utils
from solum.conductor import api as conductor_api
from solum.deployer import api as deploy_api
from solum import objects
from solum.objects import assembly
from solum.objects import image
from solum.worker import api as worker_api


LOG = logging.getLogger(__name__)

# Register options for the service
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


def list_opts():
    yield 'api', API_SERVICE_OPTS


CONF = cfg.CONF
CONF.register_opts(API_SERVICE_OPTS, group='api')

ASSEMBLY_STATES = assembly.States
IMAGE_STATES = image.States


class AssemblyHandler(handler.Handler):
    """Fulfills a request on the assembly resource."""

    def get(self, id):
        """Return an assembly."""
        return objects.registry.Assembly.get_by_uuid(self.context, id)

    def trigger_workflow(self, trigger_id, commit_sha='',
                         status_url=None, collab_url=None):
        """Get trigger by trigger id and start git workflow associated."""
        # Note: self.context will be None at this point as this is a
        # non-authenticated request.
        db_obj = objects.registry.Assembly.get_by_trigger_id(None,
                                                             trigger_id)
        try:
            # get the trust\impersonation context and authenticate it.
            self.context = keystone_utils.create_delegation_context(
                db_obj, self.context)
        except exception.AuthorizationFailure as auth_ex:
            LOG.warning(auth_ex)
            return

        plan_obj = objects.registry.Plan.get_by_id(self.context,
                                                   db_obj.plan_id)

        artifacts = plan_obj.raw_content.get('artifacts', [])
        for arti in artifacts:
            if repo_utils.verify_artifact(arti, collab_url):
                self._build_artifact(assem=db_obj, artifact=arti,
                                     commit_sha=commit_sha,
                                     status_url=status_url)

    def update(self, id, data):
        """Modify a resource."""
        updated = objects.registry.Assembly.update_and_save(self.context,
                                                            id, data)
        return updated

    def delete(self, id):
        """Delete a resource."""
        db_obj = objects.registry.Assembly.get_by_uuid(self.context, id)

        conductor_api.API(context=self.context).update_assembly(
            db_obj.id, {'status': ASSEMBLY_STATES.DELETING})

        deploy_api.API(context=self.context).destroy_assembly(
            assem_id=db_obj.id)

    def create(self, data, commit_sha='', status_url=None):
        """Create a new resource."""
        if 'workflow' in data and isinstance(data['workflow'], list):
            data['workflow'] = list(set(data['workflow']))
        else:
            data['workflow'] = ['unittest', 'build', 'deploy']
        db_obj = objects.registry.Assembly()
        db_obj.update(data)
        db_obj.uuid = uuidutils.generate_uuid()
        db_obj.user_id = self.context.user
        db_obj.project_id = self.context.project_id
        db_obj.username = self.context.user_name

        db_obj.status = ASSEMBLY_STATES.QUEUED
        db_obj.create(self.context)

        plan_obj = objects.registry.Plan.get_by_id(self.context,
                                                   db_obj.plan_id)

        artifacts = plan_obj.raw_content.get('artifacts', [])
        for arti in artifacts:
            self._build_artifact(assem=db_obj, artifact=arti,
                                 commit_sha=commit_sha,
                                 status_url=status_url)
        return db_obj

    def _build_artifact(self, assem, artifact, verb='launch_workflow',
                        commit_sha='', status_url=None):

        # This is a tempory hack so we don't need the build client
        # in the requirements.
        image = objects.registry.Image()
        image.name = artifact['name']
        image.source_uri = artifact['content']['href']
        image.base_image_id = artifact.get('language_pack', 'auto')
        image.source_format = artifact.get('artifact_type',
                                           CONF.api.source_format)
        image.image_format = CONF.api.image_format
        image.uuid = uuidutils.generate_uuid()
        image.user_id = self.context.user
        image.project_id = self.context.project_id
        image.status = IMAGE_STATES.QUEUED
        image.create(self.context)
        test_cmd = artifact.get('unittest_cmd')
        run_cmd = artifact.get('run_cmd')
        repo_token = artifact.get('repo_token')
        ports = artifact.get('ports', [80])

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

    def get_all(self):
        """Return all assemblies, based on the query provided."""
        return objects.registry.AssemblyList.get_all(self.context)
