# Copyright 2014 - Rackspace
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

from solum.api.handlers import language_pack_handler
from solum.common import exception as exc
from solum.tests import base
from solum.tests import fakes
from solum.tests import utils


@mock.patch('solum.objects.registry.Image')
class TestLanguagePackHandler(base.BaseTestCase):
    def setUp(self):
        super(TestLanguagePackHandler, self).setUp()
        self.ctx = utils.dummy_context()

    def test_languagepack_get(self, mock_img):
        mock_img.get_lp_by_name_or_uuid.return_value = {}
        handler = language_pack_handler.LanguagePackHandler(self.ctx)
        res = handler.get('test_id')
        self.assertIsNotNone(res)
        mock_img.get_lp_by_name_or_uuid.assert_called_once_with(
            self.ctx, 'test_id', include_operators_lp=True)

    def test_languagepack_get_all(self, mock_img):
        mock_img.get_by_uuid.return_value = {}
        handler = language_pack_handler.LanguagePackHandler(self.ctx)
        res = handler.get_all()
        self.assertIsNotNone(res)
        mock_img.get_all_languagepacks.assert_called_once_with(
            self.ctx)

    @mock.patch('solum.api.handlers.language_pack_handler.'
                'LanguagePackHandler._start_build')
    def test_languagepack_create(self, mock_lp_build, mock_img):
        data = {'name': 'new app',
                'source_uri': 'git://example.com/foo'}
        fi = fakes.FakeImage()
        mock_img.get_lp_by_name_or_uuid.side_effect = exc.ResourceNotFound()
        mock_img.return_value = fi
        handler = language_pack_handler.LanguagePackHandler(self.ctx)
        res = handler.create(data, lp_metadata=None)
        mock_lp_build.assert_called_once_with(res)
        fi.update.assert_called_once_with(data)
        fi.create.assert_called_once_with(self.ctx)

    @mock.patch('solum.objects.registry.PlanList')
    def test_languagepack_delete(self, mock_planlist, mock_img):
        fi = fakes.FakeImage()
        mock_img.get_lp_by_name_or_uuid.return_value = fi
        mock_img.destroy.return_value = {}
        mock_planlist.get_all.return_value = {}
        handler = language_pack_handler.LanguagePackHandler(self.ctx)
        handler.delete('test_lp')
        mock_img.get_lp_by_name_or_uuid.assert_called_once_with(
            self.ctx, 'test_lp')
        fi.destroy.assert_called_once_with(self.ctx)

    @mock.patch('solum.objects.registry.PlanList')
    def test_languagepack_delete_with_plan_using_lp(self, mock_planlist,
                                                    mock_img):
        fi = fakes.FakeImage()
        fi.name = 'test_lp'
        mock_img.get_lp_by_name_or_uuid.return_value = fi
        mock_img.destroy.return_value = {}
        mock_planlist.get_all.return_value = [fakes.FakePlan()]
        handler = language_pack_handler.LanguagePackHandler(self.ctx)
        self.assertRaises(exc.LPStillReferenced, handler.delete, 'test_lp')
        mock_img.get_lp_by_name_or_uuid.assert_called_once_with(
            self.ctx, 'test_lp')
        mock_planlist.get_all.assert_called_once()
        assert not fi.destroy.called

    @mock.patch('solum.objects.registry.PlanList')
    def test_languagepack_delete_with_plan_not_using_lp(self, mock_planlist,
                                                        mock_img):
        fi = fakes.FakeImage()
        mock_img.get_lp_by_name_or_uuid.return_value = fi
        mock_img.destroy.return_value = {}
        mock_planlist.get_all.return_value = [fakes.FakePlan()]
        handler = language_pack_handler.LanguagePackHandler(self.ctx)
        handler.delete('lp_name')
        mock_img.get_lp_by_name_or_uuid.assert_called_once_with(
            self.ctx, 'lp_name')
        mock_planlist.get_all.assert_called_once()
        fi.destroy.assert_called_once_with(self.ctx)
