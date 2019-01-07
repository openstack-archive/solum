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

"""Starter script for the Solum Worker service."""

import os
import shlex
import sys

from oslo_config import cfg
from oslo_log import log as logging
from oslo_privsep import priv_context

import solum
from solum.common.rpc import service as rpc_service
from solum.common import service
from solum.common import trace_data
from solum.common import utils
from solum.i18n import _
from solum.worker.handlers import default as default_handler
from solum.worker.handlers import noop as noop_handler
from solum.worker.handlers import shell as shell_handler

LOG = logging.getLogger(__name__)


cli_opts = [
    cfg.IntOpt('run-container-cmd-as', metavar='UID', default=65533,
               help='Run commands in containers as the user assigned '
                    'with the UID, which can be used to constrain resource, '
                    'e.g. disk usage, on a worker host.'),
]


def main():
    priv_context.init(root_helper=shlex.split(utils.get_root_helper()))
    cfg.CONF.register_cli_opts(cli_opts)
    service.prepare_service(sys.argv)
    solum.TLS.trace = trace_data.TraceData()

    LOG.info(_('Starting server in PID %s') % os.getpid())
    LOG.debug("Configuration:")
    logging.setup(cfg.CONF, 'solum')

    cfg.CONF.import_opt('topic', 'solum.worker.config', group='worker')
    cfg.CONF.import_opt('host', 'solum.worker.config', group='worker')
    cfg.CONF.import_opt('handler', 'solum.worker.config', group='worker')

    handlers = {
        'noop': noop_handler.Handler,
        'default': default_handler.Handler,
        'shell': shell_handler.Handler,
    }

    endpoints = [
        handlers[cfg.CONF.worker.handler](),
    ]

    server = rpc_service.Service(cfg.CONF.worker.topic,
                                 cfg.CONF.worker.host, endpoints)
    server.serve()
