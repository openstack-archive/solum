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
from unittest import mock
import wsme
import wsmeext.pecan as wsme_pecan

from solum.common import exception
from solum.tests import base
from solum.tests import fakes


class TestException(Exception):

    def __init__(self, *args, **kwargs):
        self.code = kwargs.pop('code', None)
        Exception.__init__(self, *args, **kwargs)


class TestPostData(wsme.types.Base):

    foo = wsme.types.text


class TestController(object):

    @exception.wrap_wsme_controller_exception
    def post(self, data):
        return self.mock_post(data)

    def mock_post(self, data):
        pass  # mock this


class TestPecanController(pecan.rest.RestController):

    @exception.wrap_pecan_controller_exception
    @pecan.expose()
    def post(self):
        return self.mock_post()

    def mock_post(self):
        pass  # mock this


class TestWsmePecanController(pecan.rest.RestController):

    @exception.wrap_wsme_pecan_controller_exception
    @wsme_pecan.wsexpose(TestPostData, body=TestPostData, status=201)
    def post(self, data):
        return self.mock_post(data)

    def mock_post(self, data):
        # mock this
        pass


@mock.patch.object(TestController, 'mock_post')
class TestWsmeExceptionWrapper(base.BaseTestCase):

    def test_wrap_500(self, mockpost):
        mockpost.__name__ = 'post'
        thrown = (TestException(code=500),
                  TestException(code=700),
                  TestException(code=1450),
                  Exception("This is an error"))
        mockpost.side_effect = [e for e in thrown]
        controller = TestController()
        for expect in thrown:
            exc = self.assertRaises(wsme.exc.ClientSideError, controller.post,
                                    'foo')
            self.assertIn('Your request could not be handled because of a '
                          'problem in the server.', str(exc))
            self.assertEqual(expect.code if hasattr(expect, 'code') else 500,
                             exc.code)

    def test_wrap_under_500(self, mockpost):
        mockpost.__name__ = 'post'
        thrown = (TestException("Test Error 1", code=400),
                  TestException("Test Error 2", code=0))
        mockpost.side_effect = [e for e in thrown]
        controller = TestController()
        for expect in thrown:
            exc = self.assertRaises(wsme.exc.ClientSideError, controller.post,
                                    'foo')
            self.assertIn(str(expect), str(exc))
            self.assertEqual(expect.code, exc.code)


@mock.patch('pecan.response', new_callable=fakes.FakePecanResponse)
@mock.patch('pecan.request', new_callable=fakes.FakePecanRequest)
@mock.patch.object(TestPecanController, 'mock_post', autospec=True)
class TestPecanExceptionWrapper(base.BaseTestCase):

    def test_wrap_500(self, mockpost, mockreq, mockresp):
        mockpost.__name__ = 'post'
        mockreq.__name__ = 'request'
        mockresp.__name__ = 'response'
        thrown = [TestException(code=500),
                  TestException(code=700),
                  TestException(code=1450),
                  Exception("This is an error")]
        mockpost.side_effect = (t for t in thrown)
        controller = TestPecanController()
        for expect in thrown:
            controller.post()
            self.assertIn('Your request could not be handled because of a '
                          'problem in the server.', mockresp.text)
            self.assertEqual(expect.code if hasattr(expect, "code") else 500,
                             mockresp.status)

    def test_wrap_under_500(self, mockpost, mockreq, mockresp):
        mockpost.__name__ = 'post'
        mockreq.__name__ = 'request'
        mockresp.__name__ = 'response'
        thrown = (TestException("Test Error 1", code=400),
                  TestException("Test Error 2", code=0))
        mockpost.side_effect = (t for t in thrown)
        controller = TestPecanController()
        for exp in thrown:
            controller.post()
            self.assertIn(str(exp), mockresp.text)
            self.assertEqual(exp.code, mockresp.status)


@mock.patch('pecan.response', new_callable=fakes.FakePecanResponse)
@mock.patch('pecan.request', new_callable=fakes.FakePecanRequest)
@mock.patch.object(TestWsmePecanController, 'mock_post', autospec=True)
class TestWsmePecanExceptionWrapper(base.BaseTestCase):

    def test_wrap_500(self, mockpost, mockreq, mockresp):
        mockpost.__name__ = 'post'
        mockreq.__name__ = 'request'
        mockresp.__name__ = 'response'
        mockresp.status_code = 500
        mockpost.side_effect = Exception("This is a hidden message")
        mockreq.body = '{"foo":"bar"}'
        mockreq.content_type = "application/json"
        resp = TestWsmePecanController().post()
        self.assertIn('Your request could not be handled because of a '
                      'problem in the server.', resp.get('faultstring'))

    def test_wrap_under_500(self, mockpost, mockreq, mockresp):
        mockpost.__name__ = 'post'
        mockreq.__name__ = 'request'
        mockresp.__name__ = 'response'
        mockpost.side_effect = exception.BadRequest(reason="Testing")
        mockreq.body = '{"foo":"bar"}'
        mockreq.content_type = "application/json"
        resp = TestWsmePecanController().post()
        self.assertEqual(exception.BadRequest.code, mockresp.status)
        self.assertIn('Testing', resp.get('faultstring'))
