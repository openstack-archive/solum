#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from io import StringIO
from requests import exceptions
from unittest import mock
import urllib

from solum.common import urlfetch
from solum.tests import base


FETCH_SIZE_OK = 500


class Response(object):
    def __init__(self, buf=''):
        self.buf = buf

    def iter_content(self, chunk_size=1):
        while self.buf:
            yield self.buf[:chunk_size]
            self.buf = self.buf[chunk_size:]

    def raise_for_status(self):
        pass


class TestUrlFetch(base.BaseTestCase):
    def setUp(self):
        super(TestUrlFetch, self).setUp()

    @mock.patch('solum.common.urlfetch.requests.get')
    def test_max_size_zero_byte(self, mock_get):
        data = '{ "foo": "bar" }'
        mock_get.return_value = Response(data)
        url = 'http://example.com/plan'
        self.assertRaises(IOError, urlfetch.get, url, 0)

    @mock.patch('solum.common.urlfetch.requests.get')
    def test_chunk_size_zero_byte(self, mock_get):
        data = '{ "foo": "bar" }'
        mock_get.return_value = Response(data)
        url = 'http://example.com/plan'
        self.assertRaises(IOError, urlfetch.get, url, FETCH_SIZE_OK, 0)

    @mock.patch('solum.common.urlfetch.requests.get')
    def test_http_scheme(self, mock_get):
        data = '{ "foo": "bar" }'
        mock_get.return_value = Response(data)
        url = 'http://example.com/plan'
        self.assertEqual(data, urlfetch.get(url, FETCH_SIZE_OK))

    @mock.patch('solum.common.urlfetch.requests.get')
    def test_https_scheme(self, mock_get):
        url = 'https://example.com/plan'
        data = '{ "foo": "bar" }'
        mock_get.return_value = Response(data)
        self.assertEqual(data, urlfetch.get(url, FETCH_SIZE_OK))

    @mock.patch('solum.common.urlfetch.requests.get')
    def test_http_error(self, mock_get):
        url = 'http://example.com/plan'
        mock_get.side_effect = IOError
        self.assertRaises(IOError, urlfetch.get, url, FETCH_SIZE_OK)

    @mock.patch('solum.common.urlfetch.requests.get')
    def test_non_exist_url(self, mock_get):
        url = 'http://non-exist.com/plan'
        mock_get.side_effect = exceptions.Timeout
        self.assertRaises(IOError, urlfetch.get, url, FETCH_SIZE_OK)

    def test_invalid_url(self):
        self.assertRaises(IOError, urlfetch.get, 'invalid_url', FETCH_SIZE_OK)

    @mock.patch('solum.common.urlfetch.requests.get')
    def test_max_fetch_size_okay(self, mock_get):
        url = 'http://example.com/plan'
        data = '{ "foo": "bar" }'
        mock_get.return_value = Response(data)
        urlfetch.get(url, FETCH_SIZE_OK)

    @mock.patch('solum.common.urlfetch.requests.get')
    def test_max_fetch_size_error(self, mock_get):
        url = 'http://example.com/plan'
        data = '{ "foo": "bar" }'
        mock_get.return_value = Response(data)
        exception = self.assertRaises(IOError, urlfetch.get, url, 5)
        self.assertIn("File exceeds", str(exception))

    def test_file_scheme_default_behaviour(self):
        self.assertRaises(IOError, urlfetch.get, 'file:///etc/profile',
                          FETCH_SIZE_OK)

    @mock.patch('urllib.request.urlopen')
    def test_file_scheme_supported(self, mock_urlopen):
        data = '{ "foo": "bar" }'
        url = 'file:///etc/profile'
        mock_urlopen.return_value = StringIO(data)
        self.assertEqual(data, urlfetch.get(url, FETCH_SIZE_OK,
                                            allowed_schemes=['file']))

    @mock.patch('urllib.request.urlopen')
    def test_file_scheme_failure(self, mock_urlopen):
        url = 'file:///etc/profile'
        mock_urlopen.side_effect = urllib.error.URLError('oops')
        self.assertRaises(IOError, urlfetch.get, url, FETCH_SIZE_OK,
                          allowed_schemes=['file'])
