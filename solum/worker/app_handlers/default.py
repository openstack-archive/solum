# Copyright 2015 - Rackspace Hosting
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

"""LP handler for building apps running on solum language packs"""

import io
import logging
import os
import random
import string

from docker import errors
from oslo_config import cfg
from oslo_log import log as os_logging

from solum.common import clients
from solum.common import solum_swiftclient
from solum.worker.app_handlers import base
from solum.worker.app_handlers import utils

from swiftclient import exceptions as swiftexp


LOG = os_logging.getLogger(__name__)

cfg.CONF.import_opt('container_mem_limit', 'solum.worker.config',
                    group='worker')
mem_limit = cfg.CONF.worker.container_mem_limit
build_timeout = cfg.CONF.worker.docker_build_timeout
UNITTEST_TIMEOUT = 1800  # 30 minutes


class DockerHandler(base.BaseHandler):

    def __init__(self, context, assembly, lp_type, image_storage):
        super(DockerHandler, self).__init__(context, assembly, image_storage)

        self.lp_type = lp_type
        self.lp = None
        self.source_sha = None
        if self.image_storage == 'glance':
            self.glance = clients.OpenStackClients(context).glance()

    def _download_lp(self, lp_obj_name, lp_img_tag, logger):
        # TODO(james_li): try cache before downloading from origin
        logger.log(logging.INFO, 'Downloading LP...')

        if self.image_storage == 'glance':
            return
        elif self.image_storage == 'docker_registry':
            return
        elif self.image_storage == 'swift':
            if self.work_dir is None:
                return
            path = '{}/lp/{}'.format(self.work_dir, lp_obj_name)
            swift = solum_swiftclient.SwiftClient(self.context)
            try:
                swift.download(path, 'solum_lp', lp_obj_name)
            except swiftexp.ClientException as e:
                LOG.error('Error in downloading LP %s, %s' %
                          (lp_obj_name, str(e)))
                logger.log(logging.ERROR, 'Downloading LP failed.')
                return

            if self._docker_load(path) != 0:
                logger.log(logging.ERROR, 'Loading docker image failed.')
                return

            logger.log(logging.INFO, 'LP downloaded and loaded successfully.')
            return lp_img_tag

    def _prepare(self, git_info, lp_obj_name, lp_img_tag, logger):
        """Create working dir and download LP only once for an app workflow."""
        if self.work_dir is None or self.source_sha is None:
            tenant = self.context.tenant
            self.work_dir = '/tmp/apps/{tenant}/{id}'.format(
                tenant=tenant, id=self.assembly.uuid)
            try:
                os.makedirs(self.work_dir)
                os.chmod(self.work_dir, 0o774)
                os.mkdir('{}/lp'.format(self.work_dir))
            except OSError as e:
                LOG.error('Error creating app dir %s, %s' %
                          (self.work_dir, str(e)))
                logger.log(logging.ERROR, 'Building app preparation failed.')
                return False

            revision = git_info.get('revision', 'master')

            head_sha = self._clone_repo(git_info['source_url'], self.work_dir,
                                        logger, revision=revision)
            if not head_sha:
                logger.log(logging.ERROR, 'Failed cloning app repo %s.' %
                           git_info['source_url'])
                return False

            self.source_sha = head_sha
            self._gen_docker_ignore(self.work_dir, 'code')

        if self.lp is None:
            self.lp = self._download_lp(lp_obj_name, lp_img_tag, logger)
            if self.lp is None:
                return False

        return True

    def build_lp(self, lp_name, git_info):
        logger = self._get_tenant_logger('language_pack')
        tenant = self.context.tenant
        ts = utils.timestamp()
        ranid = (''.join(random.choice(string.ascii_uppercase)
                 for _ in range(20)))
        self.work_dir = '/tmp/lps/{tenant}/{id}'.format(tenant=tenant,
                                                        id=ranid)
        try:
            os.makedirs(self.work_dir)
            os.chmod(self.work_dir, 0o774)
        except OSError as e:
            LOG.error('Error creating working dir %s, %s' %
                      (self.work_dir, str(e)))
            logger.log(logging.ERROR, 'Building LP preparation failed.')
            logger.upload()
            return

        revision = git_info.get('revision', 'master')
        head_sha = self._clone_repo(git_info['source_url'], self.work_dir,
                                    logger, revision=revision)
        if not head_sha:
            logger.log(logging.ERROR, 'Failed cloning LP repo %s.' %
                       git_info['source_url'])
            logger.upload()
            return

        storage_obj_name = '{name}-{ts}-{sha}'.format(name=lp_name, ts=ts,
                                                      sha=head_sha)
        lp_image_tag = '{tenant}-{obj}'.format(tenant=tenant,
                                               obj=storage_obj_name)
        dockerfile = '{}/code'.format(self.work_dir)

        logger.log(logging.INFO, 'Start building LP...')
        result = self._docker_build_with_retry(lp_image_tag, logger,
                                               path=dockerfile)
        if result != 0:
            logger.log(logging.ERROR, 'Failed building LP image.')
            logger.upload()
            return

        lp_file = '{}/{}'.format(self.work_dir, storage_obj_name)
        result = self._docker_save(lp_image_tag, lp_file)
        if result != 0:
            logger.log(logging.ERROR, 'Failed saving LP image.')
            logger.upload()
            return

        image_loc = self._persist_to_backend(lp_file, 'solum_lp',
                                             storage_obj_name, logger)
        if image_loc is None:
            logger.log(logging.ERROR, 'Failed persisting LP to backend.')
            logger.upload()
            return
        else:
            logger.log(logging.INFO, 'Successfully created LP image.')
            logger.upload()
            return (image_loc, lp_image_tag)

    def unittest_app(self, git_info, lp_obj_name, lp_img_tag, test_cmd):
        logger = self._get_tenant_logger('unittest')
        if not self._prepare(git_info, lp_obj_name, lp_img_tag, logger):
            logger.upload()
            return -1

        timeout_cmd = ('timeout --signal=SIGKILL {t}'
                       ' /bin/sh -c \"{test}\"').format(t=UNITTEST_TIMEOUT,
                                                        test=test_cmd)
        # username = (''.join(random.choice(string.ascii_lowercase)
        #                    for _ in range(8)))
        # useradd_cmd = ('useradd -s /bin/bash -u {uid} -m {uname} ||'
        #               ' usermod -d /app $(getent passwd {uid}'
        #               ' | cut -d: -f1)').format(uid=self.docker_cmd_uid,
        #                                         uname=username)

        # Will run user's arbitrary test_cmd as root in container,
        # waiting for the following docker patch to remap the root in
        # a container to an unprivileged user on host:
        # https://github.com/docker/docker/pull/12648
        # If the docker patch is finally abandoned, we should run test_cmd as
        # unprivileged by using the commented code above, in which case
        # we may want to leverage the following docker feature:
        # https://github.com/docker/docker/pull/10775/commits
        content = ('FROM {lp}\n'
                   'COPY code /app\n'
                   'WORKDIR /app\n'
                   'CMD {cmd}').format(lp=self.lp, cmd=timeout_cmd)
        df = 'Dockerfile.ut'
        fname = '{}/{}'.format(self.work_dir, df)
        try:
            with open(fname, 'w') as f:
                f.write(content)
        except OSError as e:
            LOG.error('Error in creating Dockerfile %s, %s' % (fname, str(e)))
            logger.log(logging.ERROR, 'Preparing running unittest failed')
            logger.upload()
            return -1

        logger.log(logging.INFO, 'Building image for running unittests...')
        tag = 'unittest-{}'.format(self.assembly.uuid)
        build_result = self._docker_build_with_retry(tag, logger,
                                                     path=self.work_dir,
                                                     dockerfile=df,
                                                     pull=False)
        self.images.append(tag)
        if build_result != 0:
            logger.log(logging.ERROR, 'Failed building image to run unittest.')
            logger.upload()
            return -1

        ct = None
        logger.log(logging.INFO, 'Running unittests...')
        try:
            ct = self.docker.create_container(image=tag, mem_limit=mem_limit,
                                              memswap_limit=-1)
            self.containers.append(ct)
            self.docker.start(container=ct.get('Id'))
            result = self.docker.wait(container=ct.get('Id'))
        except (errors.DockerException, errors.APIError) as e:
            LOG.error('Error running unittest, assembly: %s, %s' %
                      (self.assembly.uuid, str(e)))
            logger.log(logging.ERROR, 'Running unittest failed')
            logger.upload()
            return -1

        logger.log(logging.INFO, 'Finished unit testing with return code %s.' %
                   result)
        logger.upload()
        return result

    def build_app(self, app_name, git_info, lp_obj_name, lp_img_tag,
                  run_cmd):
        logger = self._get_tenant_logger('build')
        if not self._prepare(git_info, lp_obj_name, lp_img_tag, logger):
            logger.upload()
            return

        timeout_cmd = ('timeout --signal=SIGKILL {t} {cmd}').format(
            t=build_timeout, cmd='./build.sh')

        # username = (''.join(random.choice(string.ascii_lowercase)
        #                    for _ in range(8)))
        # useradd_cmd = ('useradd -s /bin/bash -u {uid} -m {uname} ||'
        #               ' usermod -d /app $(getent passwd {uid}'
        #               ' | cut -d: -f1)').format(uid=self.docker_cmd_uid,
        #                                         uname=username)

        # Will run user's arbitrary build.sh as root in container,
        # waiting for the following docker patch to remap the root in
        # a container to an unprivileged user on host:
        # https://github.com/docker/docker/pull/12648
        # If the docker patch is finally abandoned, we should run build.sh as
        # unprivileged by using the commented code above, in which case
        # we may want to leverage the following docker feature:
        # https://github.com/docker/docker/pull/10775/commits
        content_build = ('FROM {lp}\n'
                         'COPY code /app\n'
                         'WORKDIR /solum/bin\n'
                         'RUN chmod +x build.sh\n'
                         'CMD {cmd}').format(lp=self.lp, cmd=timeout_cmd)
        df = 'Dockerfile.build'
        fname = '{}/{}'.format(self.work_dir, df)
        try:
            with open(fname, 'w') as f:
                f.write(content_build)
        except OSError as e:
            LOG.error('Error in creating Dockerfile %s, %s' % (fname, str(e)))
            logger.log(logging.ERROR, 'Preparing building app DU image failed')
            logger.upload()
            return

        tenant = self.context.tenant
        ts = utils.timestamp()
        storage_obj_name = '{name}-{ts}-{sha}'.format(name=app_name, ts=ts,
                                                      sha=self.source_sha)
        du_image = '{tenant}-{obj}'.format(tenant=tenant,
                                           obj=storage_obj_name)
        du_image_in_build = '{img}:{tag}'.format(img=du_image, tag='build')

        logger.log(logging.INFO, 'Building DU image, preparing to run'
                                 ' build script')
        build_result = self._docker_build_with_retry(du_image_in_build, logger,
                                                     path=self.work_dir,
                                                     dockerfile=df,
                                                     pull=False)
        self.images.append(du_image_in_build)
        if build_result != 0:
            logger.log(logging.ERROR, 'Failed building DU image.')
            logger.upload()
            return

        logger.log(logging.INFO, 'Building DU image, running build script')
        ct = None
        result = -1
        try:
            ct = self.docker.create_container(image=du_image_in_build,
                                              mem_limit=mem_limit,
                                              memswap_limit=-1)
            self.containers.append(ct)
            self.docker.start(container=ct.get('Id'))
            result = self.docker.wait(container=ct.get('Id'))
        except (errors.DockerException, errors.APIError) as e:
            LOG.error('Error running build script, assembly: %s, %s' %
                      (self.assembly.uuid, str(e)))
            logger.log(logging.ERROR, 'Running build script failed')
            logger.upload()
            return

        if result != 0:
            logger.log(logging.ERROR, 'Build script returns with %s' % result)
            logger.upload()
            return

        try:
            self.docker.commit(container=ct.get('Id'), repository=du_image,
                               tag='build')
        except (errors.DockerException, errors.APIError) as e:
            LOG.error('Error committing the built image layer from build'
                      ' script, assembly: %s, %s' %
                      (self.assembly.uuid, str(e)))
            logger.log(logging.ERROR, 'Error building DU with the output'
                                      ' of build script')
            logger.upload()
            return

        content_run = ('FROM {img}\n'
                       'WORKDIR /app\n'
                       'CMD {cmd}').format(img=du_image_in_build, cmd=run_cmd)
        f = io.BytesIO(content_run.encode('utf-8'))
        build_result = self._docker_build_with_retry(du_image, logger,
                                                     fileobj=f, pull=False)
        self.images.append(du_image)
        if build_result != 0:
            logger.log(logging.ERROR, 'Failed building DU image.')
            logger.upload()
            return

        du_file = '{}/{}'.format(self.work_dir, storage_obj_name)
        result = self._docker_save(du_image, du_file)
        if result != 0:
            logger.log(logging.ERROR, 'Failed saving DU image.')
            logger.upload()
            return

        logger.log(logging.INFO, 'Persisting DU image to backend')
        image_loc = self._persist_to_backend(du_file, 'solum_du',
                                             storage_obj_name, logger)
        if image_loc is None:
            logger.log(logging.ERROR, 'Failed persist DU to backend.')
            logger.upload()
            return
        else:
            logger.log(logging.INFO, 'Successfully created DU image.')
            logger.upload()
            return (image_loc, du_image)
