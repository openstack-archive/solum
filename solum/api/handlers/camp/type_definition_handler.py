# -*- coding: utf-8 -*-
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

import json
import os

from solum.api.controllers.camp.v1_1.datamodel import type_definitions
from solum.api.handlers import handler


TYPE_DEFS = {}


class TypeDefinitionHandler(handler.Handler):
    @property
    def proj_dir(self):
        return os.path.normpath(os.path.join(os.path.dirname(__file__),
                                             '..', '..', '..', '..'))

    @staticmethod
    def as_typedef(dct):
        if 'type' in dct and dct['type'] == 'type_definition':
            return type_definitions.TypeDefinition.from_json(dct)
        else:
            return dct

    def _load_typedefs(self):
        typedef_dir_path = os.path.join(self.proj_dir, 'etc', 'solum', 'camp',
                                        'typeDefs')
        files = os.listdir(typedef_dir_path)
        for path in files:
            f = open(os.path.join(typedef_dir_path, path), 'r')
            type_d = json.load(f, object_hook=TypeDefinitionHandler.as_typedef)
            TYPE_DEFS[type_d.uri] = type_d

    def __init__(self, context):
        super(TypeDefinitionHandler, self).__init__(context)
        if len(TYPE_DEFS) == 0:
            self._load_typedefs()

    def get(self, path):
        if path in TYPE_DEFS:
            return TYPE_DEFS[path]

    def get_all(self):
        return TYPE_DEFS.values()
