# Copyright 2015 - Rackspace Hosting.
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

"""Swift Handler"""

import sys
import time

from solum.openstack.common import log as logging
import solum.uploaders.swift


LOG = logging.getLogger(__name__)

region_name = sys.argv[1]
auth_token = sys.argv[2]
storage_url = sys.argv[3]
action_to_take = sys.argv[4]
container = sys.argv[5]
app = sys.argv[6]
path = sys.argv[7]


upload_args = {'region_name': str(region_name),
               'auth_token': str(auth_token),
               'storage_url': str(storage_url),
               'container': str(container),
               'name': str(app),
               'path': str(path)}

status = 0

if action_to_take == 'upload':
    try:
        solum.uploaders.swift.SwiftUpload(**upload_args).upload_image()
    except Exception:
        time.sleep(1)
        try:
            solum.uploaders.swift.SwiftUpload(**upload_args).upload_image()
        except Exception as e:
            LOG.exception(e)
            status = 1
elif action_to_take == 'stat':
    try:
        solum.uploaders.swift.SwiftUpload(**upload_args).stat()
    except Exception:
        time.sleep(1)
        try:
            solum.uploaders.swift.SwiftUpload(**upload_args).stat()
        except Exception as e:
            LOG.exception(e)
            status = 1
else:
    status = -1

print('%s' % status)
