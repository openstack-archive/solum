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

from barbicanclient import client as barbicanclient
from glanceclient import client as glanceclient
from heatclient import client as heatclient
from unittest import mock

from keystoneclient.auth.identity import v2 as identity_v2
from keystoneclient import exceptions
from keystoneclient import session
from mistralclient.api import client as mistralclient
from neutronclient.neutron import client as neutronclient
from oslo_config import cfg
from swiftclient import client as swiftclient
from zaqarclient.queues.v1 import client as zaqarclient

from solum.common import clients
from solum.common import exception
from solum.tests import base


class ClientsTest(base.BaseTestCase):

    @mock.patch.object(clients.OpenStackClients, 'keystone')
    def test_url_for(self, mock_keystone):
        obj = clients.OpenStackClients(None)
        obj.url_for(service_type='fake_service', interface='fake_endpoint',
                    region_name='FakeRegion')

        mock_cat = mock_keystone.return_value.client.service_catalog
        mock_cat.url_for.assert_called_once_with(service_type='fake_service',
                                                 interface='fake_endpoint',
                                                 region_name='FakeRegion')

    @mock.patch.object(barbicanclient, 'Client')
    @mock.patch.object(session, 'Session')
    def test_clients_barbican(self, mock_sess, mock_call):
        # TODO(zhurong): should unskip the test
        self.skipTest('Skipping this test for bug #1686560')
        mock_sess.return_value = "keystone_session"
        mock_call.return_value = "barbican_client_handle"
        obj = clients.OpenStackClients(None)
        self.assertIsNone(obj._barbican)
        obj.barbican().admin_client
        self.assertIsNotNone(obj._barbican)
        mock_call.assert_called_once_with(session='keystone_session')

    def test_clients_barbican_noauth(self):
        self.skipTest('Skipping barbican noauth test.')
        dummy_url = 'http://server.test:5000/v2.0'
        cfg.CONF.set_override('www_authenticate_uri', dummy_url,
                              group='keystone_authtoken')
        cfg.CONF.set_override('username', 'solum',
                              group='keystone_authtoken')
        cfg.CONF.set_override('password', 'verybadpass',
                              group='keystone_authtoken')
        cfg.CONF.set_override('project_name', 'service',
                              group='keystone_authtoken')
        obj = clients.OpenStackClients(None)

        # try to create and store a secret
        try:
            bclient = obj.barbican().admin_client
            secret = bclient.secrets.create(name="test", payload="test")
            secret.store()
        except exceptions.ConnectionRefused:
            self.assertTrue(True)
        except exceptions.RequestTimeout:
            self.assertTrue(True)

    @mock.patch.object(barbicanclient, 'Client')
    @mock.patch.object(identity_v2, 'Password')
    @mock.patch.object(session, 'Session')
    def test_clients_barbican_cached(self, mock_sess, mock_auth, mock_call):
        # TODO(zhurong): should unskip the test
        self.skipTest('Skipping this test for bug #1686560')
        mock_auth.return_value = "keystone_auth_handle"
        mock_call.return_value = "barbican_client_handle"
        mock_sess.return_value = "keystone_session"
        obj = clients.OpenStackClients(None)
        barbican_admin = obj.barbican().admin_client
        barbican_admin_cached = obj.barbican().admin_client
        self.assertEqual(barbican_admin, barbican_admin_cached)
        mock_call.assert_called_once_with(session='keystone_session')

    @mock.patch.object(glanceclient, 'Client')
    @mock.patch.object(clients.OpenStackClients, 'url_for')
    def test_clients_glance(self, mock_url, mock_call):
        con = mock.MagicMock()
        con.tenant = "b363706f891f48019483f8bd6503c54d"
        con.auth_token = "3bcc3d3a03f44e3d8377f9247b0ad155"
        mock_url.return_value = "url_from_keystone"
        obj = clients.OpenStackClients(con)
        obj._glance = None
        obj.glance()
        mock_call.assert_called_once_with(
            '2', 'url_from_keystone', token='3bcc3d3a03f44e3d8377f9247b0ad155')
        mock_url.assert_called_once_with(service_type='image',
                                         interface='publicURL',
                                         region_name='RegionOne')

    def test_clients_glance_noauth(self):
        # TODO(zhurong): should unskip the test
        self.skipTest('Skipping this test for bug #1686560')
        con = mock.MagicMock()
        con.auth_token = None
        con.auth_token_info = None
        con.tenant = "b363706f891f48019483f8bd6503c54d"
        obj = clients.OpenStackClients(con)
        obj._glance = None
        self.assertRaises(exception.AuthorizationFailure, obj.glance)

    @mock.patch.object(glanceclient, 'Client')
    @mock.patch.object(clients.OpenStackClients, 'url_for')
    def test_clients_glance_cached(self, mock_url, mock_call):
        con = mock.MagicMock()
        con.tenant = "b363706f891f48019483f8bd6503c54d"
        con.auth_token = "3bcc3d3a03f44e3d8377f9247b0ad155"
        mock_url.return_value = "url_from_keystone"
        obj = clients.OpenStackClients(con)
        obj._glance = None
        glance = obj.glance()
        glance_cached = obj.glance()
        self.assertEqual(glance, glance_cached)

    @mock.patch.object(heatclient, 'Client')
    @mock.patch.object(clients.OpenStackClients, 'url_for')
    @mock.patch.object(clients.OpenStackClients, 'auth_url')
    def test_clients_heat(self, mock_auth, mock_url, mock_call):
        mock_auth.__get__ = mock.Mock(return_value="keystone_url")
        con = mock.MagicMock()
        con.tenant = "b363706f891f48019483f8bd6503c54b"
        con.auth_token = "3bcc3d3a03f44e3d8377f9247b0ad155"
        con.auth_url = "keystone_url"
        mock_url.return_value = "url_from_keystone"
        obj = clients.OpenStackClients(con)
        obj._heat = None
        obj.heat()
        mock_call.assert_called_once_with(
            '1', 'url_from_keystone', username=None,
            cert_file=None, token='3bcc3d3a03f44e3d8377f9247b0ad155',
            auth_url='keystone_url', ca_file=None, key_file=None,
            password=None, insecure=False)
        mock_url.assert_called_once_with(service_type='orchestration',
                                         interface='publicURL',
                                         region_name='RegionOne')

    def test_clients_heat_noauth(self):
        # TODO(zhurong): should unskip the test
        self.skipTest('Skipping this test for bug #1686560')
        con = mock.MagicMock()
        con.auth_token = None
        con.auth_token_info = None
        con.tenant = "b363706f891f48019483f8bd6503c54b"
        auth_url = mock.PropertyMock(name="auth_url",
                                     return_value="keystone_url")
        type(con).auth_url = auth_url
        con.get_url_for = mock.Mock(name="get_url_for")
        con.get_url_for.return_value = "url_from_keystone"
        obj = clients.OpenStackClients(con)
        obj._heat = None
        self.assertRaises(exception.AuthorizationFailure, obj.heat)

    @mock.patch.object(clients.OpenStackClients, 'url_for')
    @mock.patch.object(clients.OpenStackClients, 'auth_url')
    def test_clients_heat_cached(self, mock_auth, mock_url):
        mock_auth.__get__ = mock.Mock(return_value="keystone_url")
        con = mock.MagicMock()
        con.tenant = "b363706f891f48019483f8bd6503c54b"
        con.auth_token = "3bcc3d3a03f44e3d8377f9247b0ad155"
        con.auth_url = "keystone_url"
        mock_url.return_value = "url_from_keystone"
        obj = clients.OpenStackClients(con)
        obj._heat = None
        heat = obj.heat()
        heat_cached = obj.heat()
        self.assertEqual(heat, heat_cached)

    @mock.patch.object(swiftclient, 'Connection')
    @mock.patch.object(clients.OpenStackClients, 'url_for')
    def test_clients_swift(self, mock_url, mock_call):
        con = mock.MagicMock()
        con.tenant = "b363706f891f48019483f8bd6503c54b"
        con.auth_token = "3bcc3d3a03f44e3d8377f9247b0ad155"
        mock_url.return_value = "url_from_keystone"
        obj = clients.OpenStackClients(con)
        obj._swift = None
        obj.swift()
        mock_call.assert_called_once_with(
            auth_version="2.0",
            os_options={'endpoint_type': 'publicURL',
                        'region_name': 'RegionOne'},
            cacert=None, preauthurl="url_from_keystone", insecure=False,
            preauthtoken="3bcc3d3a03f44e3d8377f9247b0ad155")

    def test_clients_swift_noauth(self):
        # TODO(zhurong): should unskip the test
        self.skipTest('Skipping this test for bug #1686560')
        con = mock.MagicMock()
        con.auth_token = None
        con.auth_token_info = None
        con.tenant = "b363706f891f48019483f8bd6503c54b"
        auth_url = mock.PropertyMock(name="auth_url",
                                     return_value="keystone_url")
        type(con).auth_url = auth_url
        con.get_url_for = mock.Mock(name="get_url_for")
        con.get_url_for.return_value = "url_from_keystone"
        obj = clients.OpenStackClients(con)
        obj._swift = None
        self.assertRaises(exception.AuthorizationFailure, obj.swift)

    @mock.patch.object(clients.OpenStackClients, 'url_for')
    @mock.patch.object(clients.OpenStackClients, 'auth_url')
    def test_clients_swift_not_cached(self, mock_auth, mock_url):
        mock_auth.__get__ = mock.Mock(return_value="keystone_url")
        con = mock.MagicMock()
        con.tenant = "b363706f891f48019483f8bd6503c54b"
        con.auth_token = "3bcc3d3a03f44e3d8377f9247b0ad155"
        mock_url.return_value = "url_from_keystone"
        obj = clients.OpenStackClients(con)
        obj._swift = None
        swift = obj.swift()
        swift_cached = obj.swift()
        self.assertNotEqual(swift, swift_cached)

    @mock.patch.object(neutronclient, 'Client')
    @mock.patch.object(clients.OpenStackClients, 'url_for')
    @mock.patch.object(clients.OpenStackClients, 'auth_url')
    def test_clients_neutron(self, mock_auth, mock_url, mock_call):
        mock_auth.__get__ = mock.Mock(return_value="keystone_url")
        con = mock.MagicMock()
        con.tenant = "b363706f891f48019483f8bd6503c54b"
        con.auth_token = "3bcc3d3a03f44e3d8377f9247b0ad155"
        con.auth_url = "keystone_url"
        mock_url.return_value = "url_from_keystone"
        obj = clients.OpenStackClients(con)
        obj._neutron = None
        obj.neutron()
        mock_call.assert_called_once_with(
            '2.0', endpoint_url='url_from_keystone', username=None,
            token='3bcc3d3a03f44e3d8377f9247b0ad155', auth_url='keystone_url',
            ca_cert=None, password=None, insecure=False)

    def test_clients_neutron_noauth(self):
        # TODO(zhurong): should unskip the test
        self.skipTest('Skipping this test for bug #1686560')
        con = mock.MagicMock()
        con.auth_token = None
        con.auth_token_info = None
        con.tenant = "b363706f891f48019483f8bd6503c54b"
        auth_url = mock.PropertyMock(name="auth_url",
                                     return_value="keystone_url")
        type(con).auth_url = auth_url
        con.get_url_for = mock.Mock(name="get_url_for")
        con.get_url_for.return_value = "url_from_keystone"
        obj = clients.OpenStackClients(con)
        obj._neutron = None
        self.assertRaises(exception.AuthorizationFailure, obj.neutron)

    @mock.patch.object(clients.OpenStackClients, 'url_for')
    @mock.patch.object(clients.OpenStackClients, 'auth_url')
    def test_clients_neutron_cached(self, mock_auth, mock_url):
        mock_auth.__get__ = mock.Mock(return_value="keystone_url")
        con = mock.MagicMock()
        con.tenant = "b363706f891f48019483f8bd6503c54b"
        con.auth_token = "3bcc3d3a03f44e3d8377f9247b0ad155"
        mock_url.return_value = "url_from_keystone"
        obj = clients.OpenStackClients(con)
        obj._neutron = None
        neutron = obj.neutron()
        neutron_cached = obj.neutron()
        self.assertEqual(neutron, neutron_cached)

    @mock.patch.object(mistralclient, 'client')
    @mock.patch.object(clients.OpenStackClients, 'url_for')
    def test_clients_mistral(self, mock_url, mock_call):
        con = mock.MagicMock()
        con.tenant = "b363706f891f48019483f8bd6503c54d"
        con.auth_token = "3bcc3d3a03f44e3d8377f9247b0ad155"
        mock_url.return_value = "url_from_keystone"
        obj = clients.OpenStackClients(con)
        obj._mistral = None
        obj.mistral()
        mock_call.assert_called_once_with(
            mistral_url='url_from_keystone',
            auth_token='3bcc3d3a03f44e3d8377f9247b0ad155')
        mock_url.assert_called_once_with(service_type='workflow',
                                         interface='publicURL',
                                         region_name='RegionOne')

    def test_clients_mistral_noauth(self):
        # TODO(zhurong): should unskip the test
        self.skipTest('Skipping this test for bug #1686560')
        con = mock.MagicMock()
        con.auth_token = None
        con.auth_token_info = None
        con.tenant = "b363706f891f48019483f8bd6503c54d"
        obj = clients.OpenStackClients(con)
        obj._mistral = None
        self.assertRaises(exception.AuthorizationFailure, obj.mistral)

    @mock.patch.object(mistralclient, 'client')
    @mock.patch.object(clients.OpenStackClients, 'url_for')
    def test_clients_mistral_cached(self, mock_url, mock_call):
        con = mock.MagicMock()
        con.tenant = "b363706f891f48019483f8bd6503c54d"
        con.auth_token = "3bcc3d3a03f44e3d8377f9247b0ad155"
        mock_url.return_value = "url_from_keystone"
        obj = clients.OpenStackClients(con)
        obj._mistral = None
        mistral = obj.mistral()
        mistral_cached = obj.mistral()
        self.assertEqual(mistral, mistral_cached)

    @mock.patch.object(zaqarclient, 'Client')
    @mock.patch.object(clients.OpenStackClients, 'url_for')
    @mock.patch.object(clients.OpenStackClients, 'auth_url')
    def test_clients_zaqar(self, mock_auth, mock_url, mock_call):
        mock_auth.__get__ = mock.Mock(return_value="keystone_url")
        con = mock.MagicMock()
        con.tenant = "b363706f891f48019483f8bd6503c54b"
        con.auth_token = "3bcc3d3a03f44e3d8377f9247b0ad155"
        con.auth_url = "keystone_url"
        mock_url.return_value = "url_from_keystone"
        obj = clients.OpenStackClients(con)
        obj._zaqar = None
        obj.zaqar()
        conf = {'auth_opts':
                {'backend': 'keystone',
                 'options':
                    {'os_auth_token': '3bcc3d3a03f44e3d8377f9247b0ad155',
                     'os_auth_url': 'keystone_url',
                     'insecure': False}
                 }
                }
        mock_call.assert_called_once_with('url_from_keystone', conf=conf)

    def test_clients_zaqar_noauth(self):
        # TODO(zhurong): should unskip the test
        self.skipTest('Skipping this test for bug #1686560')
        con = mock.MagicMock()
        con.auth_token = None
        con.auth_token_info = None
        con.tenant = "b363706f891f48019483f8bd6503c54b"
        auth_url = mock.PropertyMock(name="auth_url",
                                     return_value="keystone_url")
        type(con).auth_url = auth_url
        con.get_url_for = mock.Mock(name="get_url_for")
        con.get_url_for.return_value = "url_from_keystone"
        obj = clients.OpenStackClients(con)
        obj._zaqar = None
        self.assertRaises(exception.AuthorizationFailure, obj.zaqar)

    @mock.patch.object(clients.OpenStackClients, 'url_for')
    @mock.patch.object(clients.OpenStackClients, 'auth_url')
    def test_clients_zaqar_cached(self, mock_auth, mock_url):
        mock_auth.__get__ = mock.Mock(return_value="keystone_url")
        con = mock.MagicMock()
        con.tenant = "b363706f891f48019483f8bd6503c54b"
        con.auth_token = "3bcc3d3a03f44e3d8377f9247b0ad155"
        mock_url.return_value = "url_from_keystone"
        obj = clients.OpenStackClients(con)
        obj._zaqar = None
        zaqar = obj.zaqar()
        zaqar_cached = obj.zaqar()
        self.assertEqual(zaqar, zaqar_cached)
