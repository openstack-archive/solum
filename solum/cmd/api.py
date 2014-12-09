# Copyright 2013 - Red Hat, Inc.
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

"""Starter script for the Solum API service."""

import logging as std_logging
import os
import sys

import eventlet
from eventlet import wsgi
from oslo.config import cfg

from solum.api import app as api_app
from solum.common import service
from solum.openstack.common.gettextutils import _
from solum.openstack.common import log as logging


LOG = logging.getLogger(__name__)


def main():
    eventlet.monkey_patch(socket=True, select=True, time=True)
    service.prepare_service(sys.argv)

    app = api_app.setup_app()

    # Create the WSGI server and start it
    host, port = cfg.CONF.api.host, cfg.CONF.api.port

    LOG.info(_('Starting server in PID %s') % os.getpid())
    LOG.debug("Configuration:")
    cfg.CONF.log_opt_values(LOG, std_logging.DEBUG)

    if host == '0.0.0.0':
        LOG.info(_('serving on 0.0.0.0:%(port)s, '
                   'view at http://127.0.0.1:%(port)s') %
                 dict(port=port))
    else:
        LOG.info(_('serving on http://%(host)s:%(port)s') %
                 dict(host=host, port=port))

    wsgi.server(eventlet.listen((host, port)), app)
