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


from solum.api.controllers.camp.v1_1.datamodel import format
from solum.api.handlers import handler


GLOBAL_FORMATS = {
    'json_format':
        format.Format(uri='json_format',
                      name='JSON',
                      type='format',
                      description="JavaScript Object Notation",
                      mime_type='application/json',
                      version='RFC4627',
                      documentation='http://www.ietf.org/rfc/rfc4627.txt')
}


class FormatHandler(handler.Handler):

    def get(self, path):
        if path in GLOBAL_FORMATS:
            return GLOBAL_FORMATS[path]
