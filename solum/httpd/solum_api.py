#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""WSGI script for solum-api.

Script for running solum-api under Apache2.
"""

from oslo_config import cfg
import oslo_i18n as i18n
from oslo_log import log as logging

from solum.api import app as api_app
from solum.common import config
from solum import objects


def init_application():
    i18n.enable_lazy()

    LOG = logging.getLogger('solum.api')

    logging.register_options(cfg.CONF)
    cfg.CONF(project='solum')
    logging.setup(cfg.CONF, 'solum')

    config.set_config_defaults()
    objects.load()

    port = cfg.CONF.api.port
    host = cfg.CONF.api.host
    LOG.info(('Starting Solum REST API on %(host)s:%(port)s'),
             {'host': host, 'port': port})
    return api_app.setup_app()
