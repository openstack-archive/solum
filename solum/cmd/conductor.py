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

"""Starter script for the Solum Conductor service."""

import os
import sys

from oslo_config import cfg
from oslo_log import log as logging

from solum.common.rpc import service as rpc_service
from solum.common import service
from solum.conductor.handlers import default as default_handler
from solum.i18n import _

LOG = logging.getLogger(__name__)


def main():
    service.prepare_service(sys.argv)

    LOG.info(_('Starting server in PID %s') % os.getpid())
    LOG.debug("Configuration:")
    logging.setup(cfg.CONF, 'solum')

    cfg.CONF.import_opt('topic', 'solum.conductor.config', group='conductor')
    cfg.CONF.import_opt('host', 'solum.conductor.config', group='conductor')
    endpoints = [
        default_handler.Handler(),
    ]
    server = rpc_service.Service(cfg.CONF.conductor.topic,
                                 cfg.CONF.conductor.host, endpoints)
    server.serve()
