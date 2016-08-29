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

import datetime as dt
import json
import logging
import time

from oslo_config import cfg
from oslo_log import log as os_logging

import solum.uploaders.local as local_uploader
import solum.uploaders.swift as swift_uploader

cfg.CONF.import_opt('log_upload_strategy', 'solum.worker.config',
                    group='worker')
LOG = os_logging.getLogger(__name__)


class TenantLogger(object):

    def __init__(self, ctxt, assem, workflow_id, deployer_log_dir, stage):
        strategy = cfg.CONF.worker.log_upload_strategy
        LOG.debug("User log upload strategy: %s" % strategy)

        self.ctxt = ctxt
        self.assem = assem
        self.stage = stage

        # Note: assembly type is used by uploader
        self.assem.type = 'app'

        tenant_log_file = "%s-%s" % (stage, workflow_id)
        self.path = "%s/%s.log" % (deployer_log_dir, tenant_log_file)
        LOG.debug("Deployer logs stored at %s" % self.path)

        uploadr = {
            'local': local_uploader.LocalStorage,
            'swift': swift_uploader.SwiftUpload,
        }.get(strategy, local_uploader.LocalStorage)

        self.uploader = uploadr(ctxt, self.path, assem, workflow_id, stage)

        self.assem_logger = logging.getLogger(workflow_id)
        self.assem_logger.setLevel(logging.DEBUG)

        self.handler = logging.FileHandler(self.path, "a", encoding=None,
                                           delay="false")
        self.handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter("%(levelname)s - %(message)s")
        self.handler.setFormatter(formatter)
        self.assem_logger.addHandler(self.handler)

    def upload(self):
        self.handler.close()
        self.uploader.upload_log()

    def log(self, level, message):
        logline = self._logline(message)
        try:
            self.assem_logger.log(level, logline)
        except IOError as e:
            LOG.error(e)

    def _logline(self, message):
        log_line = {}
        t = time.time()
        print_tm = dt.datetime.fromtimestamp(t).strftime('%Y-%m-%d %H:%M:%S')
        log_line['@timestamp'] = print_tm
        log_line['project_id'] = self.ctxt.tenant
        log_line['stage_id'] = self.assem.uuid
        log_line['task'] = self.stage
        log_line['message'] = message
        return json.dumps(log_line)
