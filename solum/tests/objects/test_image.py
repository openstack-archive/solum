# Copyright 2014 - Rackspace US, Inc.
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

from solum import objects
from solum.objects import registry
from solum.objects.sqlalchemy import image
from solum.tests import base
from solum.tests import utils


class TestImage(base.BaseTestCase):
    def setUp(self):
        super(TestImage, self).setUp()
        self.db = self.useFixture(utils.Database())
        self.ctx = utils.dummy_context()
        self.data = [{'project_id': 'test_id',
                      'user_id': 'fred',
                      'uuid': '12345678abcdefgh',
                      'name': 'image1',
                      'description': 'test image'}]
        utils.create_models_from_data(image.Image, self.data, self.ctx)

    def test_objects_registered(self):
        self.assertTrue(registry.Image)
        self.assertTrue(registry.ImageList)

    def test_get_all(self):
        lst = image.ImageList()
        self.assertEqual(1, len(lst.get_all(self.ctx)))

    def test_check_data(self):
        test_srvc = image.Image().get_by_id(self.ctx, self.data[0]['id'])
        for key, value in self.data[0].items():
            self.assertEqual(value, getattr(test_srvc, key))


class TestStates(base.BaseTestCase):
    def test_as_dict(self):
        self.assertEqual(objects.image.States.as_dict(),
                         {'BUILDING': 'BUILDING', 'COMPLETE': 'COMPLETE',
                          'ERROR': 'ERROR', 'PENDING': 'PENDING'})

    def test_values(self):
        self.assertEqual(objects.image.States.values(),
                         ['BUILDING', 'COMPLETE', 'PENDING', 'ERROR'])
