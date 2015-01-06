# Copyright 2015 - Rackspace Hosting
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

from functionaltests.api import base


class ReleaseVersionTests(base.TestCase):
    def test_release_reported(self):
        resp, body = self.client.get('/')
        release_version = resp.get('x-solum-release')
        self.assertTrue(release_version is not None)
