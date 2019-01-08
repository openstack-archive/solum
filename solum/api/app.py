#
# Copyright 2013 - Noorul Islam K M
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import os

from oslo_config import cfg
import oslo_middleware.cors as cors_middleware
import pecan

from solum.api import auth
from solum.api import config as api_config

import eventlet

if os.name == 'nt':
    # eventlet monkey patching causes subprocess.Popen to fail on Windows
    # when using pipes due to missing non blocking I/O support
    eventlet.monkey_patch(os=False)
else:
    eventlet.monkey_patch()


# Register options for the service
API_SERVICE_OPTS = [
    cfg.IntOpt('port',
               default=9777,
               help='The port for the solum API server'),
    cfg.HostAddressOpt('host',
                       default='127.0.0.1',
                       help='The listen IP for the solum API server'),
    cfg.IntOpt('max_apps_per_tenant',
               default=10,
               help='Maximum number of application allowed per tenant'),
]

API_PLAN_OPTS = [
    cfg.IntOpt('max_plan_size',
               default=65536,
               help='Maximum raw byte size of a plan'),
]


CONF = cfg.CONF
opt_group = cfg.OptGroup(name='api',
                         title='Options for the solum-api service')


def list_opts():
    yield 'api', API_SERVICE_OPTS
    yield None, API_PLAN_OPTS


CONF.register_group(opt_group)
CONF.register_opts(API_SERVICE_OPTS, opt_group)
CONF.register_opts(API_PLAN_OPTS)


def get_pecan_config():
    # Set up the pecan configuration
    filename = api_config.__file__.replace('.pyc', '.py')
    return pecan.configuration.conf_from_file(filename)


def setup_app(config=None):

    if not config:
        config = get_pecan_config()

    app_conf = dict(config.app)

    app = pecan.make_app(
        app_conf.pop('root'),
        logging=getattr(config, 'logging', {}),
        **app_conf
    )

    app = auth.install(app, CONF)

    # Create a CORS wrapper, and attach solum-specific defaults that must be
    # supported on all CORS responses.
    app = cors_middleware.CORS(app, CONF)

    return app
