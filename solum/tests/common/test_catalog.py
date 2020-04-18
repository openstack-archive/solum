# Copyright 2014 - Rackspace Hosting.
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

import os.path
from unittest import mock


from solum.common import catalog
from solum.common import exception
from solum.tests import base


class TestCatalog(base.BaseTestCase):
    def setUp(self):
        super(TestCatalog, self).setUp()
        self.proj_dir = catalog.CONF.get('source_path')
        if not self.proj_dir:
            self.proj_dir = os.path.realpath(
                os.path.join(os.path.dirname(__file__),
                             '..', '..', '..'))

    def test_get_default(self):
        with mock.patch('solum.common.catalog.open',
                        mock.mock_open(read_data='test content'),
                        create=True) as m_open:
            val = catalog.get('test', 'test_data')
            self.assertEqual('test content', val)
            expect = os.path.join(self.proj_dir,
                                  'etc/solum/test/test_data.yaml')
            m_open.assert_called_with(expect)

    def test_get_content_type(self):
        with mock.patch('solum.common.catalog.open',
                        mock.mock_open(read_data='test content'),
                        create=True) as m_open:
            val = catalog.get('test', 'test_data', content_type='fake')
            self.assertEqual('test content', val)
            expect = os.path.join(self.proj_dir,
                                  'etc/solum/test/test_data.fake')
            m_open.assert_called_with(expect)

    def test_get_fail(self):
        with mock.patch('solum.common.catalog.open',
                        mock.mock_open(read_data='test content'),
                        create=True) as m_open:
            m_open.side_effect = IOError('test')
            self.assertRaises(exception.ObjectNotFound,
                              catalog.get, 'test', 'test_data')
