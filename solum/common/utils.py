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

from cryptography.fernet import Fernet

from oslo_config import cfg
from oslo_utils import encodeutils

from solum.privileged import rootwrap as priv_rootwrap


key = Fernet.generate_key()
cipher_suite = Fernet(key)


def encrypt(value):
    ciphertext = cipher_suite.encrypt(encodeutils.safe_encode(value))
    return ciphertext


def decrypt(ciphertext):
    value = cipher_suite.decrypt(ciphertext)
    return encodeutils.safe_decode(value, 'utf-8')


def get_root_helper():
    solum_rootwrap_config = cfg.CONF.worker.rootwrap_config
    return 'sudo solum-rootwrap %s' % solum_rootwrap_config


def execute(*cmd, **kwargs):
    """Convenience wrapper around oslo's execute() method."""
    if 'run_as_root' in kwargs and 'root_helper' not in kwargs:
        kwargs['root_helper'] = get_root_helper()
    return priv_rootwrap.execute(*cmd, **kwargs)
