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

from glanceclient import client as glanceclient
from heatclient import client as heatclient
from neutronclient.neutron import client as neutronclient
from swiftclient import client as swiftclient

from solum.common import clients
from solum.common import exception
from solum.tests import base


class ClientsTest(base.BaseTestCase):

    @mock.patch.object(glanceclient, 'Client')
    def test_clients_glance(self, mock_call):
        con = mock.MagicMock()
        con.tenant = "b363706f891f48019483f8bd6503c54d"
        con.auth_token = "3bcc3d3a03f44e3d8377f9247b0ad155"
        auth_url = mock.PropertyMock(name="auth_url",
                                     return_value="keystone_url")
        type(con).auth_url = auth_url
        con.get_url_for = mock.Mock(name="get_url_for")
        con.get_url_for.return_value = "url_from_keystone"
        obj = clients.OpenStackClients(con)
        obj._glance = None
        obj.glance()
        mock_call.assert_called_once_with(
            '2', 'url_from_keystone', token='3bcc3d3a03f44e3d8377f9247b0ad155')

    def test_clients_glance_noauth(self):
        con = mock.MagicMock()
        con.auth_token = None
        con.tenant = "b363706f891f48019483f8bd6503c54d"
        auth_url = mock.PropertyMock(name="auth_url",
                                     return_value="keystone_url")
        type(con).auth_url = auth_url
        con.get_url_for = mock.Mock(name="get_url_for")
        con.get_url_for.return_value = "url_from_keystone"
        obj = clients.OpenStackClients(con)
        obj._glance = None
        self.assertRaises(exception.AuthorizationFailure, obj.glance)

    @mock.patch.object(glanceclient, 'Client')
    def test_clients_glance_cached(self, mock_call):
        con = mock.MagicMock()
        con.tenant = "b363706f891f48019483f8bd6503c54d"
        con.auth_token = "3bcc3d3a03f44e3d8377f9247b0ad155"
        auth_url = mock.PropertyMock(name="auth_url",
                                     return_value="keystone_url")
        type(con).auth_url = auth_url
        con.get_url_for = mock.Mock(name="get_url_for")
        con.get_url_for.return_value = "url_from_keystone"
        obj = clients.OpenStackClients(con)
        obj._glance = None
        glance = obj.glance()
        glance_cached = obj.glance()
        self.assertEqual(glance, glance_cached)

    @mock.patch.object(heatclient, 'Client')
    def test_clients_heat(self, mock_call):
        con = mock.MagicMock()
        con.tenant = "b363706f891f48019483f8bd6503c54b"
        con.auth_token = "3bcc3d3a03f44e3d8377f9247b0ad155"
        auth_url = mock.PropertyMock(name="auth_url",
                                     return_value="keystone_url")
        type(con).auth_url = auth_url
        con.get_url_for = mock.Mock(name="get_url_for")
        con.get_url_for.return_value = "url_from_keystone"
        obj = clients.OpenStackClients(con)
        obj._heat = None
        obj.heat()
        mock_call.assert_called_once_with(
            '1', 'url_from_keystone', username=None,
            cert_file=None, token='3bcc3d3a03f44e3d8377f9247b0ad155',
            auth_url='keystone_url', ca_file=None, key_file=None,
            password=None, insecure=False)

    def test_clients_heat_noauth(self):
        con = mock.MagicMock()
        con.auth_token = None
        con.tenant = "b363706f891f48019483f8bd6503c54b"
        auth_url = mock.PropertyMock(name="auth_url",
                                     return_value="keystone_url")
        type(con).auth_url = auth_url
        con.get_url_for = mock.Mock(name="get_url_for")
        con.get_url_for.return_value = "url_from_keystone"
        obj = clients.OpenStackClients(con)
        obj._heat = None
        self.assertRaises(exception.AuthorizationFailure, obj.heat)

    def test_clients_heat_cached(self):
        con = mock.MagicMock()
        con.tenant = "b363706f891f48019483f8bd6503c54b"
        con.auth_token = "3bcc3d3a03f44e3d8377f9247b0ad155"
        auth_url = mock.PropertyMock(name="auth_url",
                                     return_value="keystone_url")
        type(con).auth_url = auth_url
        con.get_url_for = mock.Mock(name="get_url_for")
        con.get_url_for.return_value = "url_from_keystone"
        obj = clients.OpenStackClients(con)
        obj._heat = None
        heat = obj.heat()
        heat_cached = obj.heat()
        self.assertEqual(heat, heat_cached)

    @mock.patch.object(swiftclient, 'Connection')
    def test_clients_swift(self, mock_call):
        con = mock.MagicMock()
        con.tenant = "b363706f891f48019483f8bd6503c54b"
        con.auth_token = "3bcc3d3a03f44e3d8377f9247b0ad155"
        auth_url = mock.PropertyMock(name="auth_url",
                                     return_value="keystone_url")
        type(con).auth_url = auth_url
        con.get_url_for = mock.Mock(name="get_url_for")
        con.get_url_for.return_value = "url_from_keystone"
        obj = clients.OpenStackClients(con)
        obj._swift = None
        obj.swift()
        mock_call.assert_called_once_with(
            auth_version="2.0", os_options={'endpoint_type': 'publicURL'},
            cacert=None, preauthurl="url_from_keystone", insecure=False,
            preauthtoken="3bcc3d3a03f44e3d8377f9247b0ad155")

    def test_clients_swift_noauth(self):
        con = mock.MagicMock()
        con.auth_token = None
        con.tenant = "b363706f891f48019483f8bd6503c54b"
        auth_url = mock.PropertyMock(name="auth_url",
                                     return_value="keystone_url")
        type(con).auth_url = auth_url
        con.get_url_for = mock.Mock(name="get_url_for")
        con.get_url_for.return_value = "url_from_keystone"
        obj = clients.OpenStackClients(con)
        obj._swift = None
        self.assertRaises(exception.AuthorizationFailure, obj.swift)

    def test_clients_swift_cached(self):
        con = mock.MagicMock()
        con.tenant = "b363706f891f48019483f8bd6503c54b"
        con.auth_token = "3bcc3d3a03f44e3d8377f9247b0ad155"
        auth_url = mock.PropertyMock(name="auth_url",
                                     return_value="keystone_url")
        type(con).auth_url = auth_url
        con.get_url_for = mock.Mock(name="get_url_for")
        con.get_url_for.return_value = "url_from_keystone"
        obj = clients.OpenStackClients(con)
        obj._swift = None
        swift = obj.swift()
        swift_cached = obj.swift()
        self.assertEqual(swift, swift_cached)

    @mock.patch.object(neutronclient, 'Client')
    def test_clients_neutron(self, mock_call):
        con = mock.MagicMock()
        con.tenant = "b363706f891f48019483f8bd6503c54b"
        con.auth_token = "3bcc3d3a03f44e3d8377f9247b0ad155"
        auth_url = mock.PropertyMock(name="auth_url",
                                     return_value="keystone_url")
        type(con).auth_url = auth_url
        con.get_url_for = mock.Mock(name="get_url_for")
        con.get_url_for.return_value = "url_from_keystone"
        obj = clients.OpenStackClients(con)
        obj._neutron = None
        obj.neutron()
        mock_call.assert_called_once_with(
            '2.0', endpoint_url='url_from_keystone', username=None,
            token='3bcc3d3a03f44e3d8377f9247b0ad155', auth_url='keystone_url',
            ca_cert=None, password=None, insecure=False)

    def test_clients_neutron_noauth(self):
        con = mock.MagicMock()
        con.auth_token = None
        con.tenant = "b363706f891f48019483f8bd6503c54b"
        auth_url = mock.PropertyMock(name="auth_url",
                                     return_value="keystone_url")
        type(con).auth_url = auth_url
        con.get_url_for = mock.Mock(name="get_url_for")
        con.get_url_for.return_value = "url_from_keystone"
        obj = clients.OpenStackClients(con)
        obj._neutron = None
        self.assertRaises(exception.AuthorizationFailure, obj.neutron)

    def test_clients_neutron_cached(self):
        con = mock.MagicMock()
        con.tenant = "b363706f891f48019483f8bd6503c54b"
        con.auth_token = "3bcc3d3a03f44e3d8377f9247b0ad155"
        auth_url = mock.PropertyMock(name="auth_url",
                                     return_value="keystone_url")
        type(con).auth_url = auth_url
        con.get_url_for = mock.Mock(name="get_url_for")
        con.get_url_for.return_value = "url_from_keystone"
        obj = clients.OpenStackClients(con)
        obj._neutron = None
        neutron = obj.neutron()
        neutron_cached = obj.neutron()
        self.assertEqual(neutron, neutron_cached)
