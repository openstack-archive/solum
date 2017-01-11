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


class TestSupportedFormats(base.TestCase):

    def test_formats(self):
        """Tests normative statement RE-42 from the CAMP v1.1 specification:

        http://docs.oasis-open.org/camp/camp-spec/v1.1/csprd02/
        camp-spec-v1.1-csprd02.pdf
        """
        if base.config_set_as('camp_enabled', False):
            self.skipTest('CAMP not enabled.')
        resp, body = self.client.get('camp/v1_1/formats/')
        self.assertEqual(200, resp.status, 'GET formats resource')
        formats = json.loads(body)
        self.assertEqual('formats', formats['type'])
        self.assertEqual('Solum_CAMP_formats', formats['name'])
        format_links = formats['format_links']

        # there should be one element in the Link array
        self.assertEqual(1, len(format_links), 'RE-42')
        json_link = format_links[0]
        self.assertEqual('JSON', json_link['target_name'])

        # get the URL of the platform_endpoint and strip the base URL
        url = json_link['href'][len(self.client.base_url) + 1:]

        # get our lone platform_endpoint resource
        resp, body = self.client.get(url)
        self.assertEqual(200, resp.status, 'GET JSON format resource')
        formatr = json.loads(body)
        self.assertEqual('format', formatr['type'])
        self.assertEqual('JSON', formatr['name'], 'RE-42')
        self.assertEqual('application/json', formatr['mime_type'], 'RE-42')
        self.assertEqual('RFC4627', formatr['version'], 'RE-42')
        self.assertEqual('http://www.ietf.org/rfc/rfc4627.txt',
                         formatr['documentation'],
                         'RE-42')
