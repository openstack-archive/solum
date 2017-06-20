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

"""Base LP handler for building apps"""

import errno
import io
import json
import logging
import os
import random
import string
import time

import docker
from docker import errors
from oslo_config import cfg
from oslo_log import log as os_logging
from requests.packages.urllib3 import exceptions as req_exp

from solum.common import exception as exc
from solum.common import solum_swiftclient
from solum.uploaders import tenant_logger
from solum.worker.app_handlers import utils

from swiftclient import exceptions as swiftexp


LOG = os_logging.getLogger(__name__)

cfg.CONF.import_opt('task_log_dir', 'solum.worker.config', group='worker')
cfg.CONF.import_opt('docker_daemon_url', 'solum.worker.config', group='worker')
cfg.CONF.import_opt('docker_build_timeout', 'solum.worker.config',
                    group='worker')
cfg.CONF.import_opt('container_mem_limit', 'solum.worker.config',
                    group='worker')
log_dir = cfg.CONF.worker.task_log_dir
docker_daemon_url = cfg.CONF.worker.docker_daemon_url
build_timeout = cfg.CONF.worker.docker_build_timeout
mem_limit = cfg.CONF.worker.container_mem_limit

MAX_GIT_CLONE_RETRY = 5
GIT_CLONE_TIMEOUT = 900  # 15 minutes
cloner_gid = os.getgid()


class BaseHandler(object):

    def __init__(self, context, assembly, image_storage):
        self.context = context
        self.assembly = assembly
        self.image_storage = image_storage
        self._docker = None
        self.docker_cmd_uid = cfg.CONF.run_container_cmd_as
        self.cloner_image = None
        self.images = list()
        self.containers = list()
        self.work_dir = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.close()

    @property
    def docker(self):
        if self._docker is None:
            self._docker = docker.APIClient(base_url=docker_daemon_url)
        return self._docker

    def _get_tenant_logger(self, stage):
        return tenant_logger.TenantLogger(self.context,
                                          self.assembly, log_dir, stage)

    def close(self):
        for ct in self.containers:
            if ct:
                try:
                    self.docker.remove_container(container=ct.get('Id'))
                except (errors.DockerException, errors.APIError) as e:
                    LOG.warning('Failed to remove container %s, %s' %
                                (ct.get('Id'), str(e)))

        for img in self.images:
            try:
                self.docker.remove_image(image=img, force=True)
            except (errors.DockerException, errors.APIError) as e:
                LOG.warning('Failed to remove docker image %s, %s' %
                            (img, str(e)))

        if self.work_dir:
            self._remove_cloned_repo(self.work_dir)
            try:
                utils.rm_tree(self.work_dir)
            except OSError as e:
                if e.errno != errno.ENOENT:
                    LOG.critical('critical: cannot remove dir %s,'
                                 ' disk may be full.' % self.work_dir)

        if self.cloner_image:
            try:
                self.docker.remove_image(image=self.cloner_image, force=True)
            except (errors.DockerException, errors.APIError) as e:
                LOG.error('Error in removing docker image %s, %s' %
                          (self.cloner_image, str(e)))

    def _validate_pub_repo(self, repo_url):
        pass

    @utils.retry
    def _remove_cloned_repo(self, destination):
        if not os.path.exists(destination):
            return 0

        result = 1
        try:
            ct = self.docker.create_container(
                image=self.cloner_image, user=str(self.docker_cmd_uid),
                command=['rm', '-rf', '/tmp/code'])
            self.docker.start(container=ct.get('Id'),
                              binds={destination: '/tmp'})
            result = self.docker.wait(container=ct.get('Id'))
            self.docker.remove_container(container=ct.get('Id'))
        except (errors.DockerException, errors.APIError) as e:
            clone_dir = '{}/code'.format(destination)
            LOG.error('Error in remove cloned repo %s, %s' %
                      (clone_dir, str(e)))

        return result

    def _clone_repo(self, repo_url, destination, logger, revision='master'):
        # Clone a repo with the constraints of disk and memory usage
        # Need to consider limiting network bandwidth as well.
        container_dest = '/tmp/code'
        if utils.is_git_sha(revision):
            clone_cmd = ('git clone {url} {dst} &&'
                         ' cd {dst} &&'
                         ' git checkout -B solum {rev} &&'
                         ' echo sha=$(git log -1 --pretty=%H)').format(
                url=repo_url, dst=container_dest, rev=revision)
        else:
            clone_cmd = ('git clone -b {branch} --depth 1 {url} {dst} &&'
                         ' cd {dst} &&'
                         ' echo sha=$(git log -1 --pretty=%H)').format(
                branch=revision, url=repo_url, dst=container_dest)

        timeout_clone = 'timeout --signal=SIGKILL {t} {clone}'.format(
            t=GIT_CLONE_TIMEOUT, clone=clone_cmd)

        dockerfile = ('FROM solum/cloner\n'
                      'RUN groupadd -f -g {gid} s-cloner-group\n'
                      'RUN useradd -s /bin/bash -u {uid} -g {gid} s-cloner\n'
                      'USER s-cloner\n'
                      'CMD {cmd}').format(uid=self.docker_cmd_uid,
                                          gid=cloner_gid,
                                          cmd=timeout_clone)

        ranid = ''.join(random.choice(string.digits) for _ in range(5))
        self.cloner_image = '{}-cloner-{}'.format(self.docker_cmd_uid, ranid)
        try:
            self._docker_build_with_retry(
                self.cloner_image, logger, pull=False,
                fileobj=io.BytesIO(dockerfile.encode('utf-8')))
            ct = self.docker.create_container(image=self.cloner_image,
                                              mem_limit=mem_limit,
                                              memswap_limit=-1)
        except (errors.DockerException, errors.APIError) as e:
            logger.log(logging.ERROR, 'Pre git clone stage failed.')
            LOG.error('Error in building/creating container for cloning,'
                      ' assembly: %s, %s' % (self.assembly.uuid, str(e)))
            return

        head_sha = None
        for i in range(MAX_GIT_CLONE_RETRY):
            # retry cloning
            try:
                self.docker.start(container=ct.get('Id'),
                                  binds={destination: '/tmp'})
                for line in self.docker.attach(container=ct.get('Id'),
                                               stream=True):
                    if line.startswith('sha='):
                        head_sha = line.replace('sha=', '').strip()
                    else:
                        logger.log(logging.INFO, line)
            except (errors.DockerException, errors.APIError) as e:
                logger.log(logging.ERROR, 'Got an error in cloning the repo,'
                                          ' max retry %s times. Repo: %s,'
                                          ' revision: %s' %
                           (MAX_GIT_CLONE_RETRY, repo_url, revision))
                LOG.error('Error in cloning. assembly: %s, repo: %s,'
                          ' rev: %s, %s' %
                          (self.assembly.uuid, repo_url, revision, str(e)))
            if head_sha:
                logger.log(logging.INFO, 'Finished cloning repo.')
                break
            elif i < MAX_GIT_CLONE_RETRY - 1:
                clone_dir = '{}/code'.format(destination)
                res = self._remove_cloned_repo(destination)
                if res != 0:
                    LOG.critical('critical: cannot remove dir %s,'
                                 ' disk may be full.' % clone_dir)
                time.sleep(3)

        try:
            self.docker.remove_container(container=ct.get('Id'))
        except (errors.DockerException, errors.APIError):
            pass

        return head_sha

    def _gen_docker_ignore(self, path, prefix=None):
        # Exclude .git from the docker build context
        content = '{}/.git'.format(prefix) if prefix else '.git'
        try:
            with open('{}/.dockerignore'.format(path), 'w') as f:
                f.write(content)
        except OSError:
            pass

    def _docker_build(self, tag, logger, timeout, limits, path=None,
                      dockerfile=None, fileobj=None, forcerm=True, quiet=True,
                      nocache=False, pull=True):
        success = 1
        try:
            for l in self.docker.build(path=path, dockerfile=dockerfile,
                                       fileobj=fileobj, tag=tag,
                                       timeout=timeout, forcerm=forcerm,
                                       quiet=quiet, nocache=nocache, pull=pull,
                                       container_limits=limits):
                try:
                    info = json.loads(l).get('stream', '')
                    if info:
                        if 'successfully built' in info.lower():
                            success = 0
                    else:
                        err = json.loads(l).get('errorDetail', '')
                        if err:
                            logger.log(logging.ERROR, err)
                except ValueError:
                    pass
        except req_exp.ReadTimeoutError:
            logger.log(logging.ERROR, 'docker build timed out, max value: %s' %
                       timeout)
        except (errors.DockerException, errors.APIError) as e:
            LOG.error('Error in building docker image %s, assembly: %s, %s' %
                      (tag, self.assembly.uuid, str(e)))
        return success

    def _docker_build_with_retry(self, tag, logger, path=None, dockerfile=None,
                                 fileobj=None, forcerm=True, quiet=True,
                                 limits=None, pull=True,
                                 timeout=build_timeout):
        limits = limits or {'memory': mem_limit, 'memswap': -1}

        result = self._docker_build(tag, logger, timeout, limits, path=path,
                                    dockerfile=dockerfile, fileobj=fileobj,
                                    forcerm=forcerm, quiet=quiet, pull=pull,
                                    nocache=False)
        if result == 0:
            return 0

        time.sleep(2)
        result = self._docker_build(tag, logger, timeout, limits, path=path,
                                    dockerfile=dockerfile, fileobj=fileobj,
                                    forcerm=forcerm, quiet=quiet, pull=pull,
                                    nocache=True)

        return result

    @utils.retry
    def _docker_save(self, image, output):
        result = 1
        try:
            lp = self.docker.get_image(image)
            with open(output, 'w') as f:
                f.write(lp.data)
            result = 0
        except (OSError, errors.DockerException, errors.APIError) as e:
            LOG.error('Error saving docker image, %s' % str(e))
        return result

    @utils.retry
    def _docker_load(self, path):
        result = 1
        try:
            with open(path, 'rb') as f:
                self.docker.load_image(f)
            result = 0
        except (OSError, errors.DockerException, errors.APIError) as e:
            LOG.error('Error in loading docker image, %s' % str(e))
        return result

    def _persist_to_backend(self, local_file, swift_container, swift_obj,
                            logger):
        loc = None
        if (self.image_storage == 'glance' or
                self.image_storage == 'docker_registry'):
            return loc
        elif self.image_storage == 'swift':
            swift = solum_swiftclient.SwiftClient(self.context)
            try:
                swift.upload(local_file, swift_container, swift_obj)
                loc = swift_obj
            except exc.InvalidObjectSizeError:
                logger.log(logging.INFO, 'Image with size exceeding 5GB'
                                         ' is not supported')
            except swiftexp.ClientException as e:
                LOG.error('Error in persisting artifact to swift, %s' % str(e))
            return loc

    def unittest_app(self, *args):
        """Interface to implement in derived class."""
        pass

    def build_app(self, *args):
        """Interface to implement in derived class."""
        pass
