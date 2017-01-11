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

from functionaltests.api import base


class TestTypeDefinitions(base.TestCase):

    def _test_get_resource(self, abs_url, msg, rtype, name):
        url = abs_url[len(self.client.base_url) + 1:]
        resp, body = self.client.get(url)
        self.assertEqual(200, resp.status, msg)
        resource = json.loads(body)
        self.assertEqual(rtype, resource['type'])
        self.assertEqual(name, resource['name'])
        return body

    def test_type_definitions(self):
        """Test the CAMP type_definition metadata.

        Crawls tree rooted in type_definitions and verifies that all the
        resources exist and that all the links to the attribute_definition
        resources are valid and the attribute_definitions resources exist.
        """
        if base.config_set_as('camp_enabled', False):
            self.skipTest('CAMP not enabled.')

        resp, body = self.client.get('camp/v1_1/type_definitions')
        self.assertEqual(200, resp.status, 'GET type_definitions resource')

        defs_dct = json.loads(body)
        for link_dct in defs_dct['type_definition_links']:
            msg = ("GET type_definition resource for %s" %
                   link_dct['target_name'])
            body = self._test_get_resource(link_dct['href'],
                                           msg,
                                           'type_definition',
                                           link_dct['target_name'])

            def_dct = json.loads(body)
            for adl_dct in def_dct['attribute_definition_links']:
                msg = ("GET attribute_definition resource for %s" %
                       link_dct['target_name'])
                self._test_get_resource(adl_dct['href'],
                                        msg,
                                        'attribute_definition',
                                        adl_dct['target_name'])
