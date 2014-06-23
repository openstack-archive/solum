# Copyright 2014 - Rackspace Hosting.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os.path

from solum.common import exception


def get(entity, name, content_type='yaml'):
    """This reads a file's contents from local storage.

    /etc/solum/<entity>/name.<content_type>
    """
    proj_dir = os.path.join(os.path.dirname(__file__), '..', '..')
    file_path = os.path.join(proj_dir, 'etc', 'solum', entity,
                             '%s.%s' % (name, content_type))
    try:
        with open(file_path) as fd:
            return fd.read()
    except Exception:
        raise exception.ObjectNotFound(
            name=entity, id=name)
