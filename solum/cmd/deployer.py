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

"""Starter script for the Solum Deployer service."""

import logging as std_logging
import os
import sys

from oslo.config import cfg

from solum.common.rpc import service
from solum.deployer.handlers import default as default_handler
from solum.openstack.common.gettextutils import _
from solum.openstack.common import log as logging

LOG = logging.getLogger(__name__)


def main():
    cfg.CONF(sys.argv[1:], project='solum')
    logging.setup('solum')

    LOG.info(_('Starting server in PID %s') % os.getpid())
    LOG.debug(_("Configuration:"))
    cfg.CONF.log_opt_values(LOG, std_logging.DEBUG)

    cfg.CONF.import_opt('topic', 'solum.deployer.config', group='deployer')
    cfg.CONF.import_opt('host', 'solum.deployer.config', group='deployer')
    endpoints = [
        default_handler.Handler(),
    ]
    server = service.Service(cfg.CONF.deployer.topic,
                             cfg.CONF.deployer.host, endpoints)
    server.serve()
