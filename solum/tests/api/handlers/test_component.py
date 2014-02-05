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

from solum.api.handlers import component_handler as component
from solum.tests import base


class TestComponentHandler(base.BaseTestCase):
    def test_component_get(self):
        handler = component.ComponentHandler()
        res = handler.get('test_id')
        self.assertIsNotNone(res)

    def test_component_get_all(self):
        handler = component.ComponentHandler()
        res = handler.get_all()
        self.assertIsNotNone(res)
