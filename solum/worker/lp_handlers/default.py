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

import logging
import os
import random
import string

from oslo_config import cfg

from solum.common import clients
from solum.openstack.common import log as solum_log
from solum.worker.lp_handlers import base
from solum.worker.lp_handlers import utils


LOG = solum_log.getLogger(__name__)

cfg.CONF.import_opt('container_mem_limit', 'solum.worker.config',
                    group='worker')
mem_limit = cfg.CONF.worker.container_mem_limit
UNITTEST_TIMEOUT = 1800  # 30 minutes


class DockerHandler(base.BaseHandler):

    def __init__(self, context, assembly, lp_type, image_storage):
        super(DockerHandler, self).__init__(context, assembly, image_storage)

        self.lp_type = lp_type
        self.lp = None
        if self.image_storage == 'glance':
            self.glance = clients.OpenStackClients(context).glance()

    def _download_lp(self, lp_obj_name, lp_img_tag, logger):
        # TODO(james_li): try cache before downloading from origin
        pass

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

    def unittest_app(self, *args):
        pass

    def build_app(self, *args):
        pass
