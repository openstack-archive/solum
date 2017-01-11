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

import json
import os

from solum.api.controllers.camp.v1_1.datamodel import (attribute_definitions
                                                       as model)
from solum.api.handlers import handler


ATTR_DEFS = {}


class AttributeDefinitionHandler(handler.Handler):
    @property
    def proj_dir(self):
        return os.path.normpath(os.path.join(os.path.dirname(__file__),
                                             '..', '..', '..', '..'))

    def _load_attrdefs(self):
        attrdef_dir_path = os.path.join(self.proj_dir, 'etc', 'solum', 'camp',
                                        'attributeDefs')
        for path in os.listdir(attrdef_dir_path):
            json_d = json.load(open(os.path.join(attrdef_dir_path, path), 'r'))

            # make sure this looks like an attribute definition before we
            # deserialize it
            if 'type' in json_d and json_d['type'] == 'attribute_definition':
                attr_d = model.AttributeDefinition.from_json(json_d)
                ATTR_DEFS[attr_d.uri] = attr_d

    def __init__(self, context):
        super(AttributeDefinitionHandler, self).__init__(context)
        if len(ATTR_DEFS) == 0:
            self._load_attrdefs()

    def get(self, path):
        if path in ATTR_DEFS:
            return ATTR_DEFS[path]

    def get_all(self):
        return ATTR_DEFS.values()
