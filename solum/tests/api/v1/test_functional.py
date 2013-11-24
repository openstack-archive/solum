# -*- coding: utf-8 -*-
#
# Copyright 2013 - Noorul Islam K M
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

from solum.openstack.common import jsonutils
from solum.tests.api import base
from solum import version


class TestRootController(base.FunctionalTest):

    def test_index(self):
        response = self.app.get('/', headers={'Accept': 'application/json'})
        self.assertEqual(response.status_int, 200)
        data = jsonutils.loads(response.body.decode())
        self.assertEqual(data[0]['id'], 'v1.0')
        self.assertEqual(data[0]['status'], 'CURRENT')
        self.assertEqual(data[0]['link'], {'href': 'http://localhost/v1',
                                           'targetName': 'v1'})

    def test_platform(self):
        response = self.app.get('/v1/', headers={'Accept': 'application/json'})
        self.assertEqual(response.status_int, 200)
        data = jsonutils.loads(response.body.decode())
        self.assertEqual(data['uri'], 'http://localhost/v1')
        self.assertEqual(data['name'], 'solum')
        self.assertEqual(data['description'], 'solum native implementation')
        self.assertEqual(data['implementationVersion'],
                         version.version_string())


class TestAssemblyController(base.FunctionalTest):

    def test_assemblies_get_all(self):
        response = self.app.get('/v1/assemblies',
                                headers={'Accept': 'application/json'})
        self.assertEqual(response.status_int, 200)
        data = jsonutils.loads(response.body.decode())
        self.assertEqual(data, [])


class TestServiceController(base.FunctionalTest):

    def test_services_get_all(self):
        response = self.app.get('/v1/services',
                                headers={'Accept': 'application/json'})
        self.assertEqual(response.status_int, 200)
        data = jsonutils.loads(response.body.decode())
        self.assertEqual(data['uri'], 'http://localhost/v1/services')
        self.assertEqual(data['type'], 'services')
        self.assertEqual(data['description'],
                         'The collection of available services')
        self.assertEqual(data['serviceLinks'], [])


class TestComponentController(base.FunctionalTest):

    def test_components_get_all(self):
        response = self.app.get('/v1/components',
                                headers={'Accept': 'application/json'})
        self.assertEqual(response.status_int, 200)
        data = jsonutils.loads(response.body.decode())
        self.assertEqual(data, [])


class TestExtensionController(base.FunctionalTest):

    def test_extensions_get_all(self):
        response = self.app.get('/v1/extensions',
                                headers={'Accept': 'application/json'})
        self.assertEqual(response.status_int, 200)
        data = jsonutils.loads(response.body.decode())
        self.assertEqual(data['uri'], 'http://localhost/v1/extensions')
        self.assertEqual(data['type'], 'extensions')
        self.assertEqual(data['description'], 'Collection of extensions')
        self.assertEqual(data['extensionLinks'], [])


class TestOperationController(base.FunctionalTest):

    def test_operations_get_all(self):
        response = self.app.get('/v1/operations',
                                headers={'Accept': 'application/json'})
        self.assertEqual(response.status_int, 200)
        data = jsonutils.loads(response.body.decode())
        self.assertEqual(data['uri'], 'http://localhost/v1/operations')
        self.assertEqual(data['type'], 'operations')
        self.assertEqual(data['description'], 'Collection of operations')
        self.assertEqual(data['operationLinks'], [])


class TestSensorController(base.FunctionalTest):

    def test_sensors_get_all(self):
        response = self.app.get('/v1/sensors',
                                headers={'Accept': 'application/json'})
        self.assertEqual(response.status_int, 200)
        data = jsonutils.loads(response.body.decode())
        self.assertEqual(data['uri'], 'http://localhost/v1/sensors')
        self.assertEqual(data['type'], 'sensors')
        self.assertEqual(data['description'], 'Collection of sensors')
        self.assertEqual(data['sensorLinks'], [])
