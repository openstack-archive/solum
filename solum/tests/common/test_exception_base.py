# -*- encoding: utf-8 -*-
#
# Copyright 2013 - Red Hat, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from oslo.config import cfg
import six

from solum.common import exception
from solum.tests import base


class ExceptionTestCase(base.BaseTestCase):
    """Test cases for exception code."""

    def test_with_kwargs(self):
        exc = exception.ResourceNotFound(name='application', id='green_paint')
        self.assertIn('green_paint could not be found.',
                      six.text_type(exc))
        self.assertEqual(exc.code, 404)

    def test_with_kwargs_ru(self):
        exc = exception.ResourceNotFound(name='application',
                                         id=u'зеленой_краской')
        self.assertIn(u'зеленой_краской could not be found',
                      six.text_type(exc))
        self.assertEqual(exc.code, 404)

    def test_bad_kwargs_exception(self):
        cfg.CONF.set_override('fatal_exception_format_errors', True)
        self.assertRaises(KeyError,
                          exception.ResourceNotFound, a_field='green')

    def test_bad_kwargs(self):
        cfg.CONF.set_override('fatal_exception_format_errors', False)
        exc = exception.ResourceNotFound(a_field='green')
        self.assertIn('An unknown exception occurred', six.text_type(exc))
        self.assertEqual(exc.code, 404)

    def test_resource_exists(self):
        exc = exception.ResourceExists(name='test')
        self.assertIn("The test resource already exists.",
                      six.text_type(exc))
        self.assertEqual(exc.code, 409)

    def test_application_exists(self):
        exc = exception.ResourceExists(name='test')
        self.assertIn("The test resource already exists.",
                      six.text_type(exc))
        self.assertEqual(exc.code, 409)

    def test_not_implemented(self):
        exc = exception.NotImplemented()
        self.assertIn("The requested operation is not implemented.",
                      six.text_type(exc))
        self.assertEqual(exc.code, 501)
