# Copyright (c) 2013 OpenStack Foundation
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import mock

from neutron.plugins.common import constants as p_const
from neutron.plugins.ml2.drivers import type_gre
from neutron.tests.unit.ml2 import test_type_tunnel
from neutron.tests.unit import testlib_api


TUNNEL_IP_ONE = "10.10.10.10"
TUNNEL_IP_TWO = "10.10.10.20"
HOST_ONE = 'fake_host_one'
HOST_TWO = 'fake_host_two'


class GreTypeTest(test_type_tunnel.TunnelTypeTestMixin,
                  testlib_api.SqlTestCase):
    DRIVER_CLASS = type_gre.GreTypeDriver
    TYPE = p_const.TYPE_GRE

    def test_add_endpoint(self):
        endpoint = self.driver.add_endpoint(TUNNEL_IP_ONE, HOST_ONE)
        self.assertEqual(TUNNEL_IP_ONE, endpoint.ip_address)
        self.assertEqual(HOST_ONE, endpoint.host)

    def test_add_endpoint_for_existing_tunnel_ip(self):
        self.driver.add_endpoint(TUNNEL_IP_ONE, HOST_ONE)

        with mock.patch.object(type_gre.LOG, 'warning') as log_warn:
            self.driver.add_endpoint(TUNNEL_IP_ONE, HOST_ONE)
            log_warn.assert_called_once_with(mock.ANY, TUNNEL_IP_ONE)

    def test_get_endpoint_by_host(self):
        self.driver.add_endpoint(TUNNEL_IP_ONE, HOST_ONE)

        host_endpoint = self.driver.get_endpoint_by_host(HOST_ONE)
        self.assertEqual(TUNNEL_IP_ONE, host_endpoint.ip_address)

    def test_get_endpoint_by_host_for_not_existing_host(self):
        ip_endpoint = self.driver.get_endpoint_by_host(HOST_TWO)
        self.assertIsNone(ip_endpoint)

    def test_get_endpoint_by_ip(self):
        self.driver.add_endpoint(TUNNEL_IP_ONE, HOST_ONE)

        ip_endpoint = self.driver.get_endpoint_by_ip(TUNNEL_IP_ONE)
        self.assertEqual(HOST_ONE, ip_endpoint.host)

    def test_get_endpoint_by_ip_for_not_existing_tunnel_ip(self):
        ip_endpoint = self.driver.get_endpoint_by_ip(TUNNEL_IP_TWO)
        self.assertIsNone(ip_endpoint)

    def test_get_endpoints(self):
        self.driver.add_endpoint(TUNNEL_IP_ONE, HOST_ONE)
        self.driver.add_endpoint(TUNNEL_IP_TWO, HOST_TWO)

        endpoints = self.driver.get_endpoints()
        for endpoint in endpoints:
            if endpoint['ip_address'] == TUNNEL_IP_ONE:
                self.assertEqual(HOST_ONE, endpoint['host'])
            elif endpoint['ip_address'] == TUNNEL_IP_TWO:
                self.assertEqual(HOST_TWO, endpoint['host'])

    def test_delete_endpoint(self):
        self.driver.add_endpoint(TUNNEL_IP_ONE, HOST_ONE)

        self.assertIsNone(self.driver.delete_endpoint(TUNNEL_IP_ONE))
        # Get all the endpoints and verify its empty
        endpoints = self.driver.get_endpoints()
        self.assertNotIn(TUNNEL_IP_ONE, endpoints)


class GreTypeMultiRangeTest(test_type_tunnel.TunnelTypeMultiRangeTestMixin,
                           testlib_api.SqlTestCase):
    DRIVER_CLASS = type_gre.GreTypeDriver