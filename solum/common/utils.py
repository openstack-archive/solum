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


from Crypto.Cipher import AES
from oslo_concurrency import processutils
from oslo_config import cfg


SERVICE_OPTS = [
    cfg.StrOpt('encryption_key',
               default='This is a key123',
               help=('The secret key to use in the symmetric cipher. '
                     'It must be 16 (AES-128), 24 (AES-192), '
                     'or 32 (AES-256) bytes long.')),
    cfg.StrOpt('initialization_vector',
               default='This is an IV456',
               help=('The initialization vector to use for encryption '
                     'or decryption. ')),
]

opt_group = cfg.OptGroup(
    name='encryption',
    title='Options for Encryption')


def list_opts():
    yield opt_group, SERVICE_OPTS


cfg.CONF.register_group(opt_group)
cfg.CONF.register_opts(SERVICE_OPTS, opt_group)


def encrypt(value):
    encryption_key = cfg.CONF.encryption.encryption_key
    init_vector = cfg.CONF.encryption.initialization_vector
    obj = AES.new(encryption_key, AES.MODE_CFB, init_vector)
    ciphertext = obj.encrypt(value)
    return ciphertext


def decrypt(ciphertext):
    encryption_key = cfg.CONF.encryption.encryption_key
    init_vector = cfg.CONF.encryption.initialization_vector
    obj = AES.new(encryption_key, AES.MODE_CFB, init_vector)
    value = obj.decrypt(ciphertext)
    return value


def get_root_helper():
    solum_rootwrap_config = cfg.CONF.worker.rootwrap_config
    return 'sudo solum-rootwrap %s' % solum_rootwrap_config


def execute(*cmd, **kwargs):
    """Convenience wrapper around oslo's execute() method."""
    if 'run_as_root' in kwargs and 'root_helper' not in kwargs:
        kwargs['root_helper'] = get_root_helper()
    return processutils.execute(*cmd, **kwargs)
