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

import os
import sys
from wsgiref import simple_server

from oslo.config import cfg

from solum.api import app as api_app
from solum import config
from solum.openstack.common import log as logging


LOG = logging.getLogger(__name__)


def main():
    config.parse_args(sys.argv)
    logging.setup('solum')

    app = api_app.setup_app()

    # Create the WSGI server and start it
    host, port = cfg.CONF.api.host, cfg.CONF.api.port
    srv = simple_server.make_server(host, port, app)

    LOG.info('Starting server in PID %s' % os.getpid())

    if host == '0.0.0.0':
        LOG.info('serving on 0.0.0.0:%s, view at http://127.0.0.1:%s' %
                 (port, port))
    else:
        LOG.info("serving on http://%s:%s" % (host, port))

    srv.serve_forever()
