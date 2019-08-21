# Copyright (c) 2014 Rackspace Hosting
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

import base64
import errno
import os
import shelve

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

from oslo_config import cfg
from oslo_log import log as logging
from oslo_utils import uuidutils

from solum.api.handlers import assembly_handler
from solum.api.handlers import handler
from solum.common import clients
from solum.common import exception
from solum.common import keystone_utils
from solum.common import repo_utils
from solum.deployer import api as deploy_api
from solum import objects
from solum.objects import assembly
from solum.objects import image

API_PARAMETER_OPTS = [
    cfg.StrOpt('system_param_store',
               default='database',
               help="Tells where to store system generated parameters, e.g. "
                    "deploy keys for cloning a private repo. "
                    "Options: database, barbican, local_file. "
                    "Defaults to database"),
    cfg.StrOpt('system_param_file',
               default='/etc/solum/secrets/git_secrets.db',
               help="The local file to store system generated parameters when "
                    "system_param_store is set to 'local_file'"),
]


def list_opts():
    yield 'api', API_PARAMETER_OPTS


CONF = cfg.CONF
CONF.register_opts(API_PARAMETER_OPTS, group='api')

LOG = logging.getLogger(__name__)

ASSEMBLY_STATES = assembly.States
IMAGE_STATES = image.States

sys_param_store = CONF.api.system_param_store


class PlanHandler(handler.Handler):
    """Fulfills a request on the plan resource."""

    def get(self, id):
        """Return a plan."""
        return objects.registry.Plan.get_by_uuid(self.context, id)

    def update(self, id, data):
        """Modify existing plan."""
        db_obj = objects.registry.Plan.get_by_uuid(self.context, id)
        db_obj.raw_content.update(dict((k, v) for k, v in data.items()
                                       if k != 'parameters'))
        to_update = {'raw_content': db_obj.raw_content}
        if 'name' in data:
            to_update['name'] = data['name']

        updated = objects.registry.Plan.update_and_save(self.context,
                                                        id, to_update)
        return updated

    def delete(self, id):
        """Delete existing plan."""
        db_obj = objects.registry.Plan.get_by_uuid(self.context, id)
        # Delete the trust.
        keystone_utils.delete_delegation_token(self.context, db_obj.trust_id)
        self._delete_params(db_obj.id)
        deploy_api.API(context=self.context).destroy_app(
            app_id=db_obj.id)

    def create(self, data):
        """Create a new plan."""
        db_obj = objects.registry.Plan()
        if 'name' in data:
            db_obj.name = data['name']
        db_obj.uuid = uuidutils.generate_uuid()
        db_obj.user_id = self.context.user
        db_obj.project_id = self.context.tenant
        db_obj.trigger_id = uuidutils.generate_uuid()

        # create a delegation trust_id\token, if required
        db_obj.trust_id = keystone_utils.create_delegation_token(self.context)
        db_obj.username = self.context.user_name

        sys_params = self._generate_sys_params(db_obj, data)
        user_params = data.get('parameters', {})
        self._process_ports(user_params, data)

        db_obj.raw_content = dict((k, v) for k, v in data.items()
                                  if k != 'parameters')
        db_obj.create(self.context)
        if user_params or sys_params:
            self._create_params(db_obj.id, user_params, sys_params)
        return db_obj

    def get_all(self):
        """Return all plans."""
        return objects.registry.PlanList.get_all(self.context)

    def _generate_sys_params(self, plan_obj, data):
        # NOTE: this method may modify the input 'data'
        sys_params = {}
        deploy_keys = []
        for artifact in data.get('artifacts', []):
            if (('content' not in artifact) or
                    ('private' not in artifact['content']) or
                    (not artifact['content']['private'])):
                continue
            new_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048,
                backend=default_backend()
            )
            public_key = new_key.public_key().public_bytes(
                serialization.Encoding.OpenSSH,
                serialization.PublicFormat.OpenSSH
            )
            private_key = new_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption()
            )
            artifact['content']['public_key'] = public_key
            deploy_keys.append({'source_url': artifact['content']['href'],
                                'private_key': private_key})
        if deploy_keys:
            encoded_payload = base64.b64encode(
                bytes(str(deploy_keys).encode('utf-8')))
            repo_deploy_keys = ''
            if sys_param_store == 'database':
                repo_deploy_keys = encoded_payload
            elif sys_param_store == 'local_file':
                secrets_file = CONF.api.system_param_file
                try:
                    os.makedirs(os.path.dirname(secrets_file), 0o700)
                except OSError as ex:
                    if ex.errno != errno.EEXIST:
                        raise
                s = shelve.open(secrets_file)
                try:
                    s[plan_obj.uuid] = encoded_payload
                    repo_deploy_keys = plan_obj.uuid
                finally:
                    s.close()
            elif sys_param_store == 'barbican':
                client = clients.OpenStackClients(None).barbican().admin_client
                repo_deploy_keys = client.secrets.create(
                    name=plan_obj.uuid,
                    payload=encoded_payload,
                    payload_content_type='application/octet-stream',
                    payload_content_encoding='base64').store()

            if repo_deploy_keys:
                sys_params['REPO_DEPLOY_KEYS'] = repo_deploy_keys
        return sys_params

    def _process_ports(self, user_params, data):
        # NOTE: This method may modify the input 'user_params' and 'data'
        for artifact in data.get('artifacts', []):
            new_ports = None
            ports = artifact.get('ports', [])
            if isinstance(ports, list):
                new_ports = list(it for it in set(ports) if it is not None)
            elif isinstance(ports, dict):
                new_ports = list(it for it in set(ports.values())
                                 if it is not None)
                user_params.update(dict((k, v) for k, v in ports.items()
                                        if (k and v)))
            elif type(ports) is int:
                new_ports = [ports]
            artifact['ports'] = new_ports or [80]

    def trigger_workflow(self, trigger_id, commit_sha='',
                         status_url=None, collab_url=None, workflow=None):
        """Get trigger by trigger id and start git workflow associated."""
        # Note: self.context will be None at this point as this is a
        # non-authenticated request.
        plan_obj = objects.registry.Plan.get_by_trigger_id(None, trigger_id)
        # get the trust context and authenticate it.
        try:
            self.context = keystone_utils.create_delegation_context(
                plan_obj, self.context)
            self.context.tenant = plan_obj.project_id
            self.context.user = plan_obj.user_id
            self.context.user_name = plan_obj.username

        except exception.AuthorizationFailure as auth_ex:
            LOG.warning(auth_ex)
            return

        artifacts = plan_obj.raw_content.get('artifacts', [])
        for arti in artifacts:
            if repo_utils.verify_artifact(arti, collab_url):
                self._build_artifact(plan_obj, artifact=arti,
                                     commit_sha=commit_sha,
                                     status_url=status_url,
                                     workflow=workflow)

    def _build_artifact(self, plan, artifact, verb='build', commit_sha='',
                        status_url=None, workflow=None):

        if workflow is None:
            workflow = ['unittest', 'build', 'deploy']
        ahand = assembly_handler.AssemblyHandler(self.context)
        plandata = {
            'plan_id': plan.id,
            'name': "%s-%s" % (plan.name, artifact['name']),
            'description': '',
            'workflow': workflow,
            }
        ahand.create(plandata, commit_sha=commit_sha, status_url=status_url)

    def _create_params(self, plan_id, user_params, sys_params):
        param_obj = objects.registry.Parameter()
        param_obj.plan_id = plan_id
        if user_params:
            param_obj.user_defined_params = user_params
        if sys_params:
            param_obj.sys_defined_params = sys_params
        param_obj.create(self.context)

    def _delete_params(self, plan_id):
        param_obj = objects.registry.Parameter.get_by_plan_id(self.context,
                                                              plan_id)
        if param_obj:
            sys_params = param_obj.sys_defined_params
            if sys_params and 'REPO_DEPLOY_KEYS' in sys_params:
                # sys_params['REPO_DEPLOY_KEYS'] is just a reference to
                # deploy keys when sys_param_store is not 'database'
                if sys_param_store == 'local_file':
                    secrets_file = CONF.api.system_param_file
                    s = shelve.open(secrets_file)
                    del s[sys_params['REPO_DEPLOY_KEYS'].encode("utf-8")]
                    s.close()
                elif sys_param_store == 'barbican':
                    osc = clients.OpenStackClients(None)
                    client = osc.barbican().admin_client
                    client.secrets.delete(sys_params['REPO_DEPLOY_KEYS'])

            param_obj.destroy(self.context)
