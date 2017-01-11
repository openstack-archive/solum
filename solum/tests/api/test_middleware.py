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

"""
Tests to assert that various incorporated middleware works as expected.
"""

from oslo_config import cfg
from oslo_config import fixture as config
import oslo_middleware.cors as cors_middleware
import webob

from solum.api import app as api_app
from solum.tests import base


class TestCORSMiddleware(base.BaseTestCase):
    '''Provide a basic smoke test to ensure CORS middleware is active.

    The tests below provide minimal confirmation that the CORS middleware
    is active, and may be configured. For comprehensive tests, please consult
    the test suite in oslo_middleware.
    '''

    def setUp(self):
        super(TestCORSMiddleware, self).setUp()

        # Config fixture
        self.CONF = self.useFixture(config.Config())
        # Disable keystone
        self.CONF.config(enable_authentication=False)
        # Make sure the options are registered before overriding them.
        self.CONF.register_opts(cors_middleware.CORS_OPTS, 'cors')
        # Set our test data overrides.
        self.CONF.config(allowed_origin="http://valid.example.com",
                         group='cors')

        # Initialize the conf object. Make sure we pass empty args=[], else the
        # testr CLI arguments will be picked up.
        cfg.CONF(project='solum', args=[])

        # Create the application.
        self.app = api_app.setup_app()

    def test_valid_cors_options_request(self):
        request = webob.Request.blank('/')
        request.method = 'OPTIONS'
        request.headers['Origin'] = 'http://valid.example.com'
        request.headers['Access-Control-Request-Method'] = 'GET'
        response = request.get_response(self.app)

        # Assert response status.
        self.assertEqual(200, response.status_code)
        self.assertIn('Access-Control-Allow-Origin', response.headers)
        self.assertEqual('http://valid.example.com',
                         response.headers['Access-Control-Allow-Origin'])

    def test_invalid_cors_options_request(self):
        request = webob.Request.blank('/')
        request.method = 'OPTIONS'
        request.headers['Origin'] = 'http://invalid.example.com'
        request.headers['Access-Control-Request-Method'] = 'GET'
        response = request.get_response(self.app)

        # Assert response status.
        self.assertEqual(200, response.status_code)
        self.assertNotIn('Access-Control-Allow-Origin', response.headers)

    def test_valid_cors_get_request(self):
        request = webob.Request.blank('/')
        request.method = 'GET'
        request.headers['Origin'] = 'http://valid.example.com'
        response = request.get_response(self.app)

        # Assert response status.
        self.assertEqual(200, response.status_code)
        self.assertIn('Access-Control-Allow-Origin', response.headers)
        self.assertEqual('http://valid.example.com',
                         response.headers['Access-Control-Allow-Origin'])

    def test_invalid_cors_get_request(self):
        request = webob.Request.blank('/')
        request.method = 'GET'
        request.headers['Origin'] = 'http://invalid.example.com'
        response = request.get_response(self.app)

        # Assert response status.
        self.assertEqual(200, response.status_code)
        self.assertNotIn('Access-Control-Allow-Origin', response.headers)
