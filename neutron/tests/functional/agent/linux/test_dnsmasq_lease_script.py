# Copyright (c) 2015 OpenStack Foundation.
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

import os
import subprocess
import tempfile

from neutron.agent.linux.dhcp import Dnsmasq

from neutron.tests.functional.agent.linux import base


class TestDnsmasqLeaseScript(base.BaseLinuxTestCase):

    SCRIPT = 'bin/neutron-dhcp-agent-dnsmasq-lease-init'

    def test_init(self):
        lines = ['00:00:80:aa:bb:cc, inst-name, 1.2.3.4\n',
                 '00:00:80:aa:bb:cc, inst-name,[de:ad:be::ef]\n']
        fd, hostsfile_name = tempfile.mkstemp(prefix='test-hosts', text=True)
        with file(hostsfile_name, 'w') as f:
            f.writelines(lines)
        os.close(fd)
        os.environ[Dnsmasq.HOSTS_FILE_KEY] = hostsfile_name
        try:
            output = subprocess.check_output([self.SCRIPT, 'init'])
        except Exception:
            raise
        finally:
            os.remove(hostsfile_name)

        lease = (2100 - 1970) * 365 * 24 * 3600
        self.assertEqual(
            '%s 00:00:80:aa:bb:cc 1.2.3.4 host-1-2-3-4 *\n'
            '%s 00:00:80:aa:bb:cc de:ad:be::ef host-de-ad-be--ef *\n' %
            (lease, lease),
            output)

    def test_renew(self):
        output = subprocess.check_output([self.SCRIPT, 'old'])
        self.assertEqual('', output)

    def test_hostsfile_not_exist(self):
        os.environ[Dnsmasq.HOSTS_FILE_KEY] = ''
        output = subprocess.check_output([self.SCRIPT, 'init'])
        self.assertEqual('', output)
