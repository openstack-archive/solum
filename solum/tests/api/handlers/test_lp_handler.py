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

from unittest import mock

from oslo_config import cfg

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
                'source_uri': 'git@github.com/foo/foo.git'}
        fi = fakes.FakeImage()
        cfg.CONF.set_override('max_languagepack_limit', '10',
                              group='api')
        mock_img.get_num_of_lps.return_value = 1

        mock_img.get_lp_by_name_or_uuid.side_effect = exc.ResourceNotFound()
        mock_img.return_value = fi
        handler = language_pack_handler.LanguagePackHandler(self.ctx)
        res = handler.create(data, lp_metadata=None, lp_params=None)
        mock_lp_build.assert_called_once_with(res, None)
        fi.update.assert_called_once_with(data)
        fi.create.assert_called_once_with(self.ctx)

    @mock.patch('solum.api.handlers.language_pack_handler.'
                'LanguagePackHandler._start_build')
    def test_languagepack_create_limit_reached(self, mock_lp_build,
                                               mock_img):

        data = {'name': 'new app1',
                'source_uri': 'git@github.com/foo/foo.git'}
        cfg.CONF.set_override('max_languagepack_limit', '1',
                              group='api')
        mock_img.get_num_of_lps.return_value = 1

        handler = language_pack_handler.LanguagePackHandler(self.ctx)

        self.assertRaises(exc.ResourceLimitExceeded, handler.create,
                          data, lp_metadata=None, lp_params=None)

    def test_lp_create_bad_git_url(self, mock_img):

        invalid_urls_list = list()
        invalid_urls_list.append('http://github.com/skdhfskjhdks')
        invalid_urls_list.append('github.com/abc/xyz')
        invalid_urls_list.append('xyz://github.com/abc/xyz.git')
        invalid_urls_list.append('xyz://github.com/abc/xyz')
        invalid_urls_list.append('abc')
        invalid_urls_list.append('http')
        invalid_urls_list.append('git')

        cfg.CONF.set_override('max_languagepack_limit', '10',
                              group='api')
        mock_img.get_num_of_lps.return_value = 1

        for invalid_url in invalid_urls_list:
            data = {'name': 'new app2',
                    'source_uri': invalid_url}
            handler = language_pack_handler.LanguagePackHandler(self.ctx)

            self.assertRaises(exc.BadRequest, handler.create, data,
                              lp_metadata=None, lp_params=None)

    @mock.patch('solum.common.solum_swiftclient.SwiftClient.delete_object')
    @mock.patch('solum.api.handlers.userlog_handler.UserlogHandler')
    @mock.patch('solum.objects.registry.PlanList')
    @mock.patch('solum.objects.sqlalchemy.app.App')
    def test_languagepack_delete(self, mock_app, mock_planlist,
                                 mock_log_handler,
                                 mock_swift_delete, mock_img):

        cfg.CONF.worker.image_storage = "swift"
        fi = fakes.FakeImage()
        mock_img.get_lp_by_name_or_uuid.return_value = fi
        mock_img.destroy.return_value = {}
        mock_planlist.get_all.return_value = {}

        mock_app.get_all_by_lp.return_value = {}

        handler = language_pack_handler.LanguagePackHandler(self.ctx)
        handler.delete('test_lp')

        mock_img.get_lp_by_name_or_uuid.assert_called_once_with(
            self.ctx, 'test_lp')
        docker_image_name = fi.docker_image_name
        img_filename = docker_image_name.split('-', 1)[1]
        mock_swift_delete.assert_called_once_with('solum_lp', img_filename)
        log_handler = mock_log_handler.return_value
        log_handler.delete.assert_called_once_with(fi.uuid)
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
        self.assertTrue(mock_planlist.get_all.called)
        assert not fi.destroy.called

    @mock.patch('solum.common.solum_swiftclient.SwiftClient.delete_object')
    @mock.patch('solum.api.handlers.userlog_handler.UserlogHandler')
    @mock.patch('solum.objects.registry.PlanList')
    @mock.patch('solum.objects.sqlalchemy.app.App')
    def test_languagepack_delete_with_plan_not_using_lp(self,
                                                        mock_app,
                                                        mock_planlist,
                                                        mock_log_handler,
                                                        mock_swift_delete,
                                                        mock_img):
        cfg.CONF.worker.image_storage = "swift"
        fi = fakes.FakeImage()
        mock_img.get_lp_by_name_or_uuid.return_value = fi
        mock_img.destroy.return_value = {}
        mock_planlist.get_all.return_value = [fakes.FakePlan()]

        mock_app.get_all_by_lp.return_value = {}
        handler = language_pack_handler.LanguagePackHandler(self.ctx)
        handler.delete('lp_name')

        mock_img.get_lp_by_name_or_uuid.assert_called_once_with(
            self.ctx, 'lp_name')
        docker_image_name = fi.docker_image_name
        img_filename = docker_image_name.split('-', 1)[1]
        mock_swift_delete.assert_called_once_with('solum_lp', img_filename)
        self.assertTrue(mock_planlist.get_all.called)
        log_handler = mock_log_handler.return_value
        log_handler.delete.assert_called_once_with(fi.uuid)
        fi.destroy.assert_called_once_with(self.ctx)
