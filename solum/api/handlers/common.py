# Copyright 2016 - Rackspace
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

import re

from solum.common import exception as exc


def check_url(data):
    # try to use a correct git uri
    pt = re.compile(r'^(http://|https://|git@)(.+)(/|:/)(.+)(.+)(\.git)')
    match = pt.search(data)
    if not match:
        msg = ("Bad git url. Provide git url in the following format: \n"
               "Public repo: https://github.com/<USER>/<REPO>.git\n"
               "Private repo: <http://|git@><HOST>:<USER>/<REPO>.git\n")
        raise exc.BadRequest(reason=msg)
