# Copyright 2014 - Rackspace Hosting
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

import mock
import os

from solum.builder.handlers import image_handler
from solum.tests import base
from solum.tests import fakes
from solum.tests import utils


@mock.patch('solum.objects.registry')
class TestImageHandler(base.BaseTestCase):
    def setUp(self):
        super(TestImageHandler, self).setUp()
        self.ctx = utils.dummy_context()

    def test_image_get(self, mock_registry):
        mock_registry.Image.get_by_uuid.return_value = {}
        handler = image_handler.ImageHandler(self.ctx)
        res = handler.get('test_id')
        self.assertIsNotNone(res)
        mock_registry.Image.get_by_uuid.\
            assert_called_once_with(self.ctx, 'test_id')

    @mock.patch('solum.builder.handlers.image_handler.'
                'ImageHandler._start_build')
    def test_image_create(self, mock_build, mock_registry):
        data = {'name': 'new app',
                'source_uri': 'git://example.com/foo'}
        handler = image_handler.ImageHandler(self.ctx)
        res = handler.create(data)
        self.assertEqual('new app', res.name)
        self.assertEqual('git://example.com/foo', res.source_uri)
        mock_build.assert_called_once_with(res)

    @mock.patch('subprocess.Popen')
    def test_start_build(self, mock_popen, not_used):
        handler = image_handler.ImageHandler(self.ctx)
        fim = fakes.FakeImage()
        fim.name = 'new_app'
        fim.source_format = 'heroku'
        fim.image_format = 'docker'
        fim.source_uri = 'git://example.com/foo'
        mock_popen.communicate.return_value = 'glance_id=1-2-34'
        handler._start_build(fim)
        proj_dir = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                '..', '..', '..', '..'))
        script = os.path.join(proj_dir, 'contrib/lp-cedarish/docker/build-app')
        mock_popen.assert_called_once_with([script, 'git://example.com/foo',
                                            'new_app', self.ctx.tenant,
                                            '1-2-3-4'], stdout=-1)
        expected = [mock.call(self.ctx), mock.call(self.ctx)]
        self.assertEqual(expected, fim.save.call_args_list)
