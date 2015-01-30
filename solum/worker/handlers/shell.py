# Copyright 2014 - Rackspace Hosting
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

"""Solum Worker shell handler."""

import ast
import base64
import os
import random
import shelve
import string
import subprocess

from oslo.config import cfg

import solum
from solum.common import clients
from solum.common import exception
from solum.common import repo_utils
from solum.common import solum_keystoneclient
from solum.conductor import api as conductor_api
from solum.deployer import api as deployer_api
from solum import objects
from solum.objects import assembly
from solum.objects import image
from solum.openstack.common import log as logging
from solum.openstack.common import uuidutils
import solum.uploaders.common as uploader_common
import solum.uploaders.local as local_uploader
import solum.uploaders.swift as swift_uploader


LOG = logging.getLogger(__name__)

ASSEMBLY_STATES = assembly.States
IMAGE_STATES = image.States

cfg.CONF.import_opt('task_log_dir', 'solum.worker.config', group='worker')
cfg.CONF.import_opt('proj_dir', 'solum.worker.config', group='worker')
cfg.CONF.import_opt('param_file_path', 'solum.worker.config', group='worker')
cfg.CONF.import_opt('log_upload_strategy', 'solum.worker.config',
                    group='worker')
cfg.CONF.import_opt('image_storage', 'solum.worker.config', group='worker')


def upload_task_log(ctxt, original_path, assembly, build_id, stage):
    strategy = cfg.CONF.worker.log_upload_strategy
    LOG.debug("User log upload strategy: %s" % strategy)

    uploader = {
        'local': local_uploader.LocalStorage,
        'swift': swift_uploader.SwiftUpload,
    }.get(strategy, uploader_common.UploaderBase)
    uploader(ctxt, original_path, assembly, build_id, stage).upload()


def job_update_notification(ctxt, build_id, state=None, description=None,
                            created_image_id=None, assembly_id=None):
    """send a status update to the conductor."""
    LOG.debug('build id:%s %s (%s) %s %s' % (build_id, state, description,
                                             created_image_id, assembly_id),
              context=solum.TLS.trace)
    conductor_api.API(context=ctxt).build_job_update(build_id, state,
                                                     description,
                                                     created_image_id,
                                                     assembly_id)


def get_assembly_by_id(ctxt, assembly_id):
    return solum.objects.registry.Assembly.get_by_id(ctxt, assembly_id)


def get_parameter_by_assem_id(ctxt, assembly_id):
    assem = get_assembly_by_id(ctxt, assembly_id)
    param_obj = solum.objects.registry.Parameter.get_by_plan_id(ctxt,
                                                                assem.plan_id)
    return param_obj


def update_assembly_status(ctxt, assembly_id, status):
    if assembly_id is None:
        return
    LOG.debug('Updating assembly %s status to %s' % (assembly_id, status))
    data = {'status': status}
    conductor_api.API(context=ctxt).update_assembly(assembly_id, data)


def update_lp_status(ctxt, image_id, status, external_ref=None):
    if image_id is None:
        return
    LOG.debug('Updating languagepack %s status to %s and external_ref to %s'
              % (image_id, status, external_ref))
    conductor_api.API(context=ctxt).update_image(image_id, status,
                                                 external_ref)


class Handler(object):
    def echo(self, ctxt, message):
        LOG.debug("%s" % message)

    @exception.wrap_keystone_exception
    def _get_environment(self, ctxt, source_uri, assembly_id=None,
                         test_cmd=None, run_cmd=None):
        kc = solum_keystoneclient.KeystoneClientV3(ctxt)
        image_url = kc.client.service_catalog.url_for(
            service_type='image',
            endpoint_type='publicURL')

        # create a minimal environment
        user_env = {}
        for var in ['PATH', 'LOGNAME', 'LANG', 'HOME', 'USER', 'TERM']:
            if var in os.environ:
                user_env[var] = os.environ[var]
        user_env['OS_AUTH_TOKEN'] = ctxt.auth_token
        user_env['OS_AUTH_URL'] = ctxt.auth_url
        user_env['OS_IMAGE_URL'] = image_url

        if assembly_id is not None:
            assem = get_assembly_by_id(ctxt, assembly_id)
            user_env['ASSEMBLY_ID'] = str(assem.uuid)
        else:
            str_assem = (''.join(random.choice(string.ascii_uppercase)
                         for i in range(10)))
            user_env['ASSEMBLY_ID'] = str_assem

        user_env['IMAGE_STORAGE'] = cfg.CONF.worker.image_storage

        if cfg.CONF.worker.image_storage == 'docker_registry':
            if cfg.CONF.worker.docker_reg_endpoint is None:
                LOG.debug("DU upload set to docker registry,")
                LOG.debug("but docker registry endpoint is not set.")
                LOG.debug("Setting it to 127.0.0.1")
                cfg.CONF.worker.docker_reg_endpoint = '127.0.0.1'
            user_env['DOCKER_REGISTRY'] = cfg.CONF.worker.docker_reg_endpoint

        if test_cmd is not None:
            user_env['TEST_CMD'] = test_cmd
        if run_cmd is not None:
            user_env['RUN_CMD'] = run_cmd

        user_env['PROJECT_ID'] = ctxt.tenant

        user_env['BUILD_ID'] = uuidutils.generate_uuid()
        user_env['SOLUM_TASK_DIR'] = cfg.CONF.worker.task_log_dir

        params_env = self._get_parameter_env(ctxt, source_uri, assembly_id,
                                             user_env['BUILD_ID'])
        user_env.update(params_env)
        return user_env

    @property
    def proj_dir(self):
        if cfg.CONF.worker.proj_dir:
            return cfg.CONF.worker.proj_dir
        return os.path.abspath(os.path.join(os.path.dirname(__file__),
                                            '..', '..', '..'))

    def _get_build_command(self, ctxt, stage, source_uri, name,
                           base_image_id, source_format, image_format,
                           commit_sha, artifact_type=None, lp_name=None):

        # map the input formats to script paths.
        # TODO(asalkeld) we need an "auto".
        pathm = {'heroku': 'lp-cedarish',
                 'dib': 'diskimage-builder',
                 'dockerfile': 'lp-dockerfile',
                 'chef': 'lp-chef',
                 'docker': 'docker',
                 'qcow2': 'docker',
                 'vm': 'docker'}
        if base_image_id == 'auto' and image_format == 'qcow2':
            base_image_id = 'cedarish'
        build_app_path = os.path.join(self.proj_dir, 'contrib',
                                      pathm.get(source_format, 'lp-cedarish'),
                                      pathm.get(image_format, 'docker'))

        if artifact_type == 'language_pack':
            build_lp = os.path.join(build_app_path, 'build-lp')
            return [build_lp, source_uri, name, ctxt.tenant]

        if stage == 'unittest':
            build_app = os.path.join(build_app_path, 'unittest-app')
            return [build_app, source_uri, commit_sha, ctxt.tenant,
                    base_image_id, lp_name]
        elif stage == 'build':
            build_app = os.path.join(build_app_path, 'build-app')
            return [build_app, source_uri, name, ctxt.tenant, base_image_id,
                    lp_name]

    def _get_parameter_env(self, ctxt, source_uri, assembly_id, build_id):
        param_env = {}
        if assembly_id is None:
            return param_env

        param_obj = get_parameter_by_assem_id(ctxt, assembly_id)
        if param_obj is None:
            return param_env

        user_param_file = '/'.join([cfg.CONF.worker.param_file_path,
                                    build_id, 'user_params'])
        solum_param_file = '/'.join([cfg.CONF.worker.param_file_path,
                                     build_id, 'solum_params'])
        try:
            os.makedirs(os.path.dirname(user_param_file), 0o700)
        except OSError as ex:
            LOG.error("Error creating dirs to write out param files, %s" % ex)
            return param_env

        def _sanitize_param(s):
            if type(s) in [str, unicode]:
                # Handles the case of exporting a var with a multi-line string
                return ''.join(['"', s.strip('\n').replace('"', '\\"'), '"'])
            else:
                return str(s)

        with open(user_param_file, 'w') as f:
            f.write("#!/bin/bash\n")
            if param_obj.user_defined_params:
                for k, v in param_obj.user_defined_params.items():
                    if k and k.startswith('_SYSTEM'):
                        # Variables for control purpose, e.g. _SYSTEM_USE_DRONE
                        param_env[k] = _sanitize_param(v)
                    else:
                        f.write("export %s=%s\n" % (k, _sanitize_param(v)))
        with open(solum_param_file, 'w') as f:
            f.write("#!/bin/bash\n")
            if param_obj.sys_defined_params:
                for k, v in param_obj.sys_defined_params.items():
                    if k == 'REPO_DEPLOY_KEYS':
                        # Pass in deploy key as an environment variable
                        param_env[k] = self._get_private_key(v, source_uri)
                    f.write("export %s=%s\n" % (k, _sanitize_param(v)))

        param_env['USER_PARAMS'] = user_param_file
        param_env['SOLUM_PARAMS'] = solum_param_file
        return param_env

    def build(self, ctxt, build_id, git_info, name, base_image_id,
              source_format, image_format, assembly_id,
              test_cmd, run_cmd, artifact_type=None):
        if artifact_type == 'language_pack':
            self.build_lp(ctxt, build_id, git_info, name, source_format,
                          image_format, artifact_type)
            return

        # TODO(datsun180b): This is only temporary, until Mistral becomes our
        # workflow engine.
        if self._run_unittest(ctxt, build_id, git_info, name, base_image_id,
                              source_format, image_format, assembly_id,
                              test_cmd) != 0:
            return

        update_assembly_status(ctxt, assembly_id, ASSEMBLY_STATES.BUILDING)

        solum.TLS.trace.clear()
        solum.TLS.trace.import_context(ctxt)

        source_uri = git_info['source_url']

        lp_name = ''
        if base_image_id is not 'auto':
            image = objects.registry.Image.get_by_uuid(ctxt, base_image_id)
            base_image_id = image.external_ref
            lp_name = image.name

        build_cmd = self._get_build_command(ctxt, 'build', source_uri,
                                            name, base_image_id,
                                            source_format, image_format, '',
                                            artifact_type, lp_name=lp_name)
        solum.TLS.trace.support_info(build_cmd=' '.join(build_cmd),
                                     assembly_id=assembly_id)

        try:
            user_env = self._get_environment(ctxt, source_uri,
                                             assembly_id=assembly_id,
                                             test_cmd=test_cmd,
                                             run_cmd=run_cmd)
        except exception.SolumException as env_ex:
            LOG.exception(env_ex)
            job_update_notification(ctxt, build_id, IMAGE_STATES.ERROR,
                                    description=str(env_ex),
                                    assembly_id=assembly_id)

        log_env = user_env.copy()
        if 'OS_AUTH_TOKEN' in log_env:
            del log_env['OS_AUTH_TOKEN']
        solum.TLS.trace.support_info(environment=log_env)

        job_update_notification(ctxt, build_id, IMAGE_STATES.BUILDING,
                                description='Starting the image build',
                                assembly_id=assembly_id)
        # TODO(datsun180b): Associate log with assembly properly
        logpath = "%s/%s-%s.log" % (user_env['SOLUM_TASK_DIR'],
                                    'build',
                                    user_env['BUILD_ID'])
        LOG.debug("Build logs stored at %s" % logpath)
        out = None
        assem = None
        if assembly_id is not None:
            assem = get_assembly_by_id(ctxt, assembly_id)
            if assem.status == ASSEMBLY_STATES.DELETING:
                return

        try:
            out = subprocess.Popen(build_cmd,
                                   env=user_env,
                                   stdout=subprocess.PIPE).communicate()[0]
        except (OSError, ValueError) as subex:
            LOG.exception(subex)
            job_update_notification(ctxt, build_id, IMAGE_STATES.ERROR,
                                    description=str(subex),
                                    assembly_id=assembly_id)
            update_assembly_status(ctxt, assembly_id, ASSEMBLY_STATES.ERROR)
            return

        if assem is not None:
            upload_task_log(ctxt, logpath, assem, user_env['BUILD_ID'],
                            'build')

        # we expect one line in the output that looks like:
        # created_image_id=<the glance_id>
        created_image_id = None
        for line in out.split('\n'):
            if 'created_image_id' in line:
                solum.TLS.trace.support_info(build_out_line=line)
                created_image_id = line.split('=')[-1].strip()
        if not created_image_id:
            job_update_notification(ctxt, build_id, IMAGE_STATES.ERROR,
                                    description='image not created',
                                    assembly_id=assembly_id)
            update_assembly_status(ctxt, assembly_id, ASSEMBLY_STATES.ERROR)
            return
        job_update_notification(ctxt, build_id, IMAGE_STATES.COMPLETE,
                                description='built successfully',
                                created_image_id=created_image_id,
                                assembly_id=assembly_id)
        if created_image_id is not None:
            deployer_api.API(context=ctxt).deploy(assembly_id=assembly_id,
                                                  image_id=created_image_id)
        else:
            update_assembly_status(ctxt, assembly_id, ASSEMBLY_STATES.ERROR)

    def _run_unittest(self, ctxt, build_id, git_info, name, base_image_id,
                      source_format, image_format, assembly_id,
                      test_cmd):
        if test_cmd is None:
            LOG.debug("Unit test command is None; skipping unittests.")
            return 0

        commit_sha = git_info.get('commit_sha', '')
        status_url = git_info.get('status_url')
        repo_token = git_info.get('repo_token')

        LOG.debug("Running unittests.")
        update_assembly_status(ctxt, assembly_id, ASSEMBLY_STATES.UNIT_TESTING)

        lp_name = ''
        if base_image_id is not 'auto':
            image = objects.registry.Image.get_by_uuid(ctxt, base_image_id)
            base_image_id = image.external_ref
            lp_name = image.name

        git_url = git_info['source_url']
        command = self._get_build_command(ctxt, 'unittest', git_url, name,
                                          base_image_id,
                                          source_format, image_format,
                                          commit_sha, lp_name=lp_name)

        solum.TLS.trace.clear()
        solum.TLS.trace.import_context(ctxt)

        user_env = self._get_environment(ctxt, git_url,
                                         assembly_id=assembly_id,
                                         test_cmd=test_cmd)
        log_env = user_env.copy()
        if 'OS_AUTH_TOKEN' in log_env:
            del log_env['OS_AUTH_TOKEN']
        solum.TLS.trace.support_info(environment=log_env)

        logpath = "%s/%s-%s.log" % (user_env['SOLUM_TASK_DIR'],
                                    'unittest',
                                    user_env['BUILD_ID'])
        LOG.debug("Unittest logs stored at %s" % logpath)

        returncode = -1
        assem = None
        if assembly_id is not None:
            assem = get_assembly_by_id(ctxt, assembly_id)
            if assem.status == ASSEMBLY_STATES.DELETING:
                return returncode

        try:
            runtest = subprocess.Popen(command, env=user_env,
                                       stdout=subprocess.PIPE)
            returncode = runtest.wait()
        except OSError as subex:
            LOG.exception("Exception running unit tests:")
            LOG.exception(subex)

        if assem is not None:
            upload_task_log(ctxt, logpath, assem, user_env['BUILD_ID'],
                            'unittest')

        if returncode > 0:
            LOG.error("Unit tests failed. Return code is %r" % (returncode))
            update_assembly_status(ctxt, assembly_id,
                                   ASSEMBLY_STATES.UNIT_TESTING_FAILED)
        elif returncode < 0:
            LOG.error("Error running unit tests.")
            update_assembly_status(ctxt, assembly_id, ASSEMBLY_STATES.ERROR)

        repo_utils.send_status(returncode, status_url, repo_token)

        return returncode

    def unittest(self, ctxt, build_id, git_info, name, base_image_id,
                 source_format, image_format, assembly_id,
                 test_cmd):
        self._run_unittest(ctxt, build_id, git_info, name, base_image_id,
                           source_format, image_format, assembly_id,
                           test_cmd)

    def _get_private_key(self, source_creds, source_url):
        source_private_key = ''
        if source_creds:
            cfg.CONF.import_opt('system_param_store',
                                'solum.api.handlers.plan_handler',
                                group='api')
            store = cfg.CONF.api.system_param_store

            if store == 'database':
                deploy_keys_str = base64.b64decode(source_creds)
            elif store == 'barbican':
                client = clients.OpenStackClients(None).barbican().admin_client
                secret = client.secrets.get(secret_ref=source_creds)
                deploy_keys_str = secret.payload
            elif store == 'local_file':
                cfg.CONF.import_opt('system_param_file',
                                    'solum.api.handlers.plan_handler',
                                    group='api')
                secrets_file = cfg.CONF.api.system_param_file
                s = shelve.open(secrets_file)
                deploy_keys_str = s[str(source_creds)]
                deploy_keys_str = base64.b64decode(deploy_keys_str)
                s.close()
            deploy_keys = ast.literal_eval(deploy_keys_str)
            for dk in deploy_keys:
                if source_url == dk['source_url']:
                    source_private_key = dk['private_key']
        return source_private_key

    def build_lp(self, ctxt, image_id, git_info, name, source_format,
                 image_format, artifact_type=None):
        update_lp_status(ctxt, image_id, IMAGE_STATES.BUILDING)
        source_uri = git_info['source_url']
        build_cmd = self._get_build_command(ctxt, 'build', source_uri,
                                            name, str(image_id),
                                            source_format, 'docker', '',
                                            artifact_type)

        try:
            user_env = self._get_environment(ctxt, source_uri)
        except exception.SolumException as env_ex:
            LOG.exception(_("Failed to successfully get environment for "
                            "building languagepack: `%s`"),
                          image_id)
            LOG.exception(env_ex)

        out = None
        try:
            out = subprocess.Popen(build_cmd,
                                   env=user_env,
                                   stdout=subprocess.PIPE).communicate()[0]
        except OSError as subex:
            update_lp_status(ctxt, image_id, IMAGE_STATES.ERROR)
            LOG.exception(_("Failed to successfully build languagepack: `%s`"),
                          image_id)
            LOG.exception(subex)
            return

        # we expect one line in the output that looks like:
        # image_external_ref=<external storage ref>
        image_external_ref = None
        for line in out.split('\n'):
            if 'image_external_ref' in line:
                solum.TLS.trace.support_info(build_lp_out_line=line)
                image_external_ref = line.split('=')[-1].strip()
                break
        if image_external_ref is not None:
            update_lp_status(ctxt, image_id, IMAGE_STATES.COMPLETE,
                             image_external_ref)
        else:
            update_lp_status(ctxt, image_id, IMAGE_STATES.ERROR)
