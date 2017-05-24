# Copyright 2013 - Noorul Islam K M
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

import pecan
import pecan.testing

from solum.tests import base

__all__ = ['FunctionalTest']


class FunctionalTest(base.BaseTestCase):
    """Used for functional tests.

    Where you need to test your literal application and its
    integration with the framework.
    """

    def setUp(self):
        super(FunctionalTest, self).setUp()
        self.addCleanup(pecan.set_config, {}, overwrite=True)
        self.app = pecan.testing.load_test_app({
            'app': {
                'root': 'solum.api.controllers.root.RootController',
                'modules': ['solum.api'],
                'debug': False
            }
        })

    def assertResourceNotFound(self, url):
        resp = self.app.get(url, status=404,
                            headers={'Accept': 'application/json'})
        self.assertEqual(404, resp.status_int)
