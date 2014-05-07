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

import json
import mock

from solum.builder.controllers.v1 import image
from solum.common import exception
from solum import objects
from solum.tests import base
from solum.tests import fakes


@mock.patch('pecan.request', new_callable=fakes.FakePecanRequest)
@mock.patch('pecan.response', new_callable=fakes.FakePecanResponse)
@mock.patch('solum.builder.handlers.image_handler.ImageHandler')
class TestImageController(base.BaseTestCase):
    def setUp(self):
        super(TestImageController, self).setUp()
        objects.load()

    def test_image_get(self, ImageHandler, resp_mock, request_mock):
        hand_get = ImageHandler.return_value.get
        hand_get.return_value = fakes.FakeImage()
        cont = image.ImageController('test_id')
        cont.get()
        hand_get.assert_called_with('test_id')
        self.assertEqual(200, resp_mock.status)

    def test_image_get_not_found(self, ImageHandler, resp_mock, request_mock):
        hand_get = ImageHandler.return_value.get
        hand_get.side_effect = exception.ResourceNotFound(name='image',
                                                          image_id='test_id')
        cont = image.ImageController('test_id')
        cont.get()
        hand_get.assert_called_with('test_id')
        self.assertEqual(404, resp_mock.status)


class TestImageAsDict(base.BaseTestCase):

    scenarios = [
        ('none', dict(data=None)),
        ('one', dict(data={'name': 'foo'})),
        ('full', dict(data={'uri': 'http://example.com/v1/images/x1',
                            'name': 'Example-Image',
                            'type': 'image',
                            'tags': ['small'],
                            'project_id': '1dae5a09ef2b4d8cbf3594b0eb4f6b94',
                            'user_id': '55f41cf46df74320b9486a35f5d28a11',
                            'description': 'A image'}))
    ]

    def test_as_dict(self):
        if self.data is None:
            s = image.Image()
            self.data = {}
        else:
            s = image.Image(**self.data)
        # remove fields that are only in the API model and
        # not in the db model so we can assertEqual()
        if 'uri' in self.data:
            del self.data['uri']
        if 'type' in self.data:
            del self.data['type']
        self.assertEqual(self.data, s.as_dict(objects.registry.Image))


@mock.patch('pecan.request', new_callable=fakes.FakePecanRequest)
@mock.patch('pecan.response', new_callable=fakes.FakePecanResponse)
@mock.patch('solum.builder.handlers.image_handler.ImageHandler')
class TestImagesController(base.BaseTestCase):
    def setUp(self):
        super(TestImagesController, self).setUp()
        objects.load()

    def test_post(self, ImagesHandler, resp_mock, request_mock):
        json_create = {'name': 'foo'}
        request_mock.body = json.dumps(json_create)
        request_mock.content_type = 'application/json'
        hand_create = ImagesHandler.return_value.create
        hand_create.return_value = fakes.FakeImage()
        image.ImagesController().post()
        hand_create.assert_called_with(json_create)
        self.assertEqual(201, resp_mock.status)
