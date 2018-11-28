#
# This code is part of Ansible, but is an independent component.
#
# This particular file snippet, and this file snippet only, is BSD licensed.
# Modules you write using this snippet, which is embedded dynamically by Ansible
# still belong to the author of the module, and may assign their own license
# to the complete work.
#
# (c) 2017 Red Hat, Inc.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above copyright notice,
#      this list of conditions and the following disclaimer in the documentation
#      and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE
# USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
import re

from ansible.module_utils.six import iteritems
from ansible.module_utils.network.common.utils import to_list
from ansible.module_utils.network.common.providers import register_provider
from ansible.module_utils.network.common.providers import CliProvider


@register_provider('eos', 'net_system')
class Provider(CliProvider):
    """ Arista EOS System config provider
    """

    def render(self, config=None):
        commands = list()

        if self.params['operation'] == 'replace':
            config = None

        for key, value in iteritems(self.params['config']):
            if value is not None:
                meth = getattr(self, '_render_%s' % key, None)
                if meth:
                    resp = meth(config)
                    if resp:
                        commands.extend(to_list(resp))

        return commands

    def _render_hostname(self, config=None):
        cmd = 'hostname %s' % self.params['config']['hostname']
        if not config or cmd not in config:
            return cmd

    def _render_domain_name(self, config=None):
        cmd = 'ip domain-name %s' % self.params['config']['domain_name']
        if not config or cmd not in config:
            return cmd

    def _render_routing(self, config=None):
        cmd = 'ip routing'
        if self.params['config']['routing'] is True:
            if not config or cmd not in config:
                return cmd
        elif self.params['config']['routing'] is False:
            if not config or cmd in config:
                return 'no %s' % cmd

    def _render_name_servers(self, config=None):
        commands = list()

        if config:
            matches = re.findall('ip name-server vrf (\S+) (\S+)', config, re.M)
            if matches:
                for vrf, srv in matches:
                    if srv not in self.params['config']['name_servers'] or vrf != 'default':
                        cmd = 'no ip name-server vrf %s %s' % (vrf, srv)
                        commands.append(cmd)

        for item in self.params['config']['name_servers']:
            cmd = 'ip name-server vrf default %s' % item
            if not config or cmd not in config:
                commands.append(cmd)

        return commands

    def _render_lookup_source(self, config=None):
        cmd = 'ip domain lookup source-interface %s' % self.params['config']['lookup_source']
        if not config or cmd not in config:
            return cmd

    def _render_domain_search(self, config=None):
        cmd = 'ip domain-list %s'
        commands = [cmd % item for item in self.params['config']['domain_search']]
        if not config or cmd not in config:
            return commands
