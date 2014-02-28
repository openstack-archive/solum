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

from solum.builder.handlers import image_handler
from solum.tests import base


@mock.patch('solum.objects.registry')
class TestImageHandler(base.BaseTestCase):
    def test_image_get(self, mock_registry):
        mock_registry.Image.get_by_uuid.return_value = {}
        handler = image_handler.ImageHandler()
        res = handler.get('test_id')
        self.assertIsNotNone(res)
        mock_registry.Image.get_by_uuid.\
            assert_called_once_with(None, 'test_id')

    @mock.patch('solum.builder.handlers.image_handler.'
                'ImageHandler._start_build')
    def test_image_create(self, mock_build, mock_registry):
        data = {'user_id': 'new_user_id'}
        handler = image_handler.ImageHandler()
        res = handler.create(data)
        self.assertEqual('new_user_id', res.user_id)
        mock_build.assert_called_once_with(res)
