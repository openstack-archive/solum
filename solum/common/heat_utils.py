# Copyright 2014 - Rackspace Hosting
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.


def get_network_parameters(osc):
    # TODO(julienvey) In the long term, we should have optional parameters
    # if the user wants to override this default behaviour
    params = {}
    tenant_networks = osc.neutron().list_networks()
    for tenant_network in tenant_networks['networks']:
        if tenant_network['router:external']:
            params['public_net'] = tenant_network['id']
        else:
            params['private_net'] = tenant_network['id']
            # Note (devkulkarni): Neutron subnet may contain
            # ipv6 and ipv4 subnets. We want to pick the ipv4 subnet
            params['private_subnet'] = get_ipv4_subnet_id(osc, tenant_network)
    return params


def get_ipv4_subnet_id(osc, tenant_network):
    for tenant_sub_id in tenant_network['subnets']:
        subnet_data = osc.neutron().show_subnet(tenant_sub_id)
        if subnet_data['subnet']['ip_version'] == 4:
            return tenant_sub_id
