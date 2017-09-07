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

"""Config options for Solum Worker service."""


from oslo_config import cfg

SERVICE_OPTS = [
    cfg.StrOpt('topic',
               default='solum-worker',
               help='The queue to add build tasks to'),
    cfg.HostAddressOpt('host',
                       default='localhost',
                       help='The location of the build rpc queue'),
    cfg.StrOpt('handler',
               default='shell',
               help='The worker endpoint to employ'),
    cfg.StrOpt('task_log_dir',
               default='/var/log/solum/worker',
               help='The directory containing task log output.'),
    cfg.StrOpt('proj_dir',
               default='',
               help=('The directory containing the project\'s code, '
                     'especially the contrib directory.')),
    cfg.StrOpt('log_url_prefix',
               default='http://localhost/',
               help='The prefix of test log URL to be sent back'),
    cfg.StrOpt('log_upload_strategy',
               default='local',
               help=('Upload task log to central storage, using modules like '
                     'swift and local from solum/uploaders.')),
    cfg.StrOpt('log_upload_swift_container',
               default='solum-logs',
               help='The name of the Swift container to upload logs to.'),
    cfg.StrOpt('param_file_path',
               default='/tmp/solum',
               help='The path of param files to save to.'),
    cfg.StrOpt('image_storage',
               default='glance',
               help='Image storage backend. This includes images created '
               'for LanguagePacks and Deployment Units. Possible values are '
               'docker_registry, swift and glance.'),
    cfg.StrOpt('docker_reg_endpoint',
               default="127.0.0.1",
               help='Docker registry endpoint'),
    cfg.StrOpt('delete_local_cache',
               default="false",
               help='Delete cached docker images and git repos from '
               'the worker node after building languagepacks and deployment '
               'units. Valid options are true or false.'),
    cfg.StrOpt('region_name',
               default="RegionOne",
               help='Region name to use'),
    cfg.StrOpt('temp_url_secret',
               default="secret",
               help='Secret to use with temp url'),
    cfg.StrOpt('temp_url_protocol',
               default="http",
               help='Protocol to use with temp url. Options are '
                    'http/https'),
    cfg.StrOpt('temp_url_ttl',
               default="604800",
               help='TTL in seconds.'),
    cfg.StrOpt('lp_location_url',
               default="",
               help='url to the container where LPs are stored.'),
    cfg.StrOpt('operator_lp_download_strategy',
               default="swift-client",
               help='Options for downloading operator LPs.'
               'Possible values are "wget" or "swift-client"'),
    cfg.StrOpt('lp_operator_user',
               default="demo",
               help='LP operator username.'),
    cfg.StrOpt('lp_operator_password',
               default="solum",
               help='LP operator password.'),
    cfg.StrOpt('lp_operator_tenant_name',
               default="demo",
               help='LP operator tenant name.'),
    cfg.StrOpt('docker_daemon_url',
               default="unix://var/run/docker.sock",
               help='docker daemon url.'),
    cfg.IntOpt('container_mem_limit', default=0,
               help='max memory a container can consume. No limit by default'),
    cfg.IntOpt('docker_build_timeout', default=1800,
               help='max time a docker build can take. Default: 30 minutes'),
    cfg.StrOpt('rootwrap_config',
               default='/etc/solum/rootwrap.conf',
               help='Path to the rootwrap configuration file to use for '
                    'running commands as root.'),
]

opt_group = cfg.OptGroup(
    name='worker',
    title='Options for the solum-worker service')


def list_opts():
    yield opt_group, SERVICE_OPTS


cfg.CONF.register_group(opt_group)
cfg.CONF.register_opts(SERVICE_OPTS, opt_group)
