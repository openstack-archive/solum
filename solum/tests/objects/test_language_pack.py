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

from solum.common import exception
from solum.objects import registry
from solum.objects.sqlalchemy import language_pack as lp
from solum.tests import base
from solum.tests import utils


class TestLanguagePack(base.BaseTestCase):
    def setUp(self):
        super(TestLanguagePack, self).setUp()
        self.db = self.useFixture(utils.Database())
        self.ctx = utils.dummy_context()

        attr_dict = {}
        attr_dict["runtime_versions"] = ["1.6", "1.7"]
        attr_dict["build_tool_chain"] = [{"type": "ant", "version": "1.7"},
                                         {"type": "maven", "version": "1.2"}]
        attr_dict["attributes"] = {"optional_attr1": "value",
                                   "admin_email": "someadmin@somewhere.com"}

        self.data = [{'project_id': 'test_id',
                      'user_id': 'fred',
                      'uuid': '123456789abcdefghi',
                      'name': 'languagepack1',
                      'description': 'test language pack',
                      'attr_blob': attr_dict}]

        utils.create_models_from_data(lp.LanguagePack, self.data, self.ctx)

    def test_objects_registered(self):
        self.assertTrue(registry.LanguagePack)
        self.assertTrue(registry.LanguagePackList)

    def test_get_all(self):
        lst = lp.LanguagePackList()
        self.assertEqual(1, len(lst.get_all(self.ctx)))

    def test_check_data(self):
        test_lp = lp.LanguagePack().get_by_id(self.ctx, self.data[0]['id'])
        for key, value in self.data[0].items():
            self.assertEqual(value, getattr(test_lp, key))

    def _get_flat_versions(self, language_packs):
        versions = []
        for compiler_version in language_packs.compiler_versions:
            versions.append(compiler_version.version)
        return versions

    def test_update_compiler_versions_add(self):
        data = {'compiler_versions': ['1.4', '1.5', '1.6']}
        language_pack = lp.LanguagePack()
        language_pack.compiler_versions = []
        language_pack._update_compiler_versions(data)
        self.assertEqual(len(language_pack.compiler_versions), 3)
        self.assertIn('1.4', self._get_flat_versions(language_pack))
        self.assertIn('1.5', self._get_flat_versions(language_pack))
        self.assertIn('1.6', self._get_flat_versions(language_pack))

    def test_update_compiler_versions_delete(self):
        data = {'compiler_versions': []}
        language_pack = lp.LanguagePack()
        v14 = lp.CompilerVersions()
        v14.version = '1.4'
        v15 = lp.CompilerVersions()
        v15.version = '1.5'
        v16 = lp.CompilerVersions()
        v16.version = '1.6'
        language_pack.compiler_versions = [v14, v15, v16]
        language_pack._update_compiler_versions(data)
        self.assertEqual(len(language_pack.compiler_versions), 0)

    def test_update_compiler_versions_modify(self):
        data = {'compiler_versions': ['1.4', '1.7']}
        language_pack = lp.LanguagePack()
        v14 = lp.CompilerVersions()
        v14.version = '1.4'
        v15 = lp.CompilerVersions()
        v15.version = '1.5'
        v16 = lp.CompilerVersions()
        v16.version = '1.6'
        language_pack.compiler_versions = [v14, v15, v16]
        language_pack._update_compiler_versions(data)
        self.assertEqual(len(language_pack.compiler_versions), 2)
        self.assertIn('1.4', self._get_flat_versions(language_pack))
        self.assertIn('1.7', self._get_flat_versions(language_pack))

    def test_update_compiler_versions_duplicates(self):
        data = {'compiler_versions': ['1.4', '1.4', '1.5']}
        language_pack = lp.LanguagePack()
        language_pack.compiler_versions = []
        language_pack._update_compiler_versions(data)
        self.assertEqual(len(language_pack.compiler_versions), 2)
        self.assertIn('1.4', self._get_flat_versions(language_pack))
        self.assertIn('1.5', self._get_flat_versions(language_pack))

    def test_update_os_platform_create(self):
        data = {'os_platform': {'OS': 'ubuntu', 'version': '12.04'}}
        language_pack = lp.LanguagePack()
        language_pack.os_platform = None
        language_pack._update_os_platform(data)
        self.assertIsNotNone(language_pack.os_platform)
        self.assertEqual(language_pack.os_platform.os, 'ubuntu')
        self.assertEqual(language_pack.os_platform.version, '12.04')

    def test_update_os_platform_delete_when_os_platform_not_specified(self):
        data = {}
        language_pack = lp.LanguagePack()
        lp_os_platform = lp.OSPlatform()
        lp_os_platform.os = 'ubuntu'
        lp_os_platform.version = '12.04'
        language_pack.os_platform = lp_os_platform
        language_pack._update_os_platform(data)
        self.assertIsNone(language_pack.os_platform)

    def test_update_os_platform_delete_when_os_platform_is_empty(self):
        data = {'os_platform': {}}
        language_pack = lp.LanguagePack()
        lp_os_platform = lp.OSPlatform()
        lp_os_platform.os = 'ubuntu'
        lp_os_platform.version = '12.04'
        language_pack.os_platform = lp_os_platform
        language_pack._update_os_platform(data)
        self.assertIsNone(language_pack.os_platform)

    def test_update_os_platform_update(self):
        data = {'os_platform': {'OS': 'fedora', 'version': '17'}}
        language_pack = lp.LanguagePack()
        lp_os_platform = lp.OSPlatform()
        lp_os_platform.os = 'ubuntu'
        lp_os_platform.version = '12.04'
        language_pack.os_platform = lp_os_platform
        language_pack._update_os_platform(data)
        self.assertIsNotNone(language_pack.os_platform)
        self.assertEqual(language_pack.os_platform.os, 'fedora')
        self.assertEqual(language_pack.os_platform.version, '17')

    def test_update_os_platform_bad_request(self):
        data = {'os_platform': {'OS': 'fedora', 'versasdsadion': '17'}}
        language_pack = lp.LanguagePack()
        language_pack.os_platform = None
        self.assertRaises(exception.BadRequest,
                          language_pack._update_os_platform,
                          data)
