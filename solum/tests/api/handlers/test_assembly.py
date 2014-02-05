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

from solum.api.handlers import assembly_handler as assembly
from solum.tests import base


class TestAssemblyHandler(base.BaseTestCase):
    def test_assembly_get(self):
        handler = assembly.AssemblyHandler()
        res = handler.get('test_id')
        self.assertIsNotNone(res)

    def test_assembly_get_all(self):
        handler = assembly.AssemblyHandler()
        res = handler.get_all()
        self.assertIsNotNone(res)
