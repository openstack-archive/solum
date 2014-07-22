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
            params['private_subnet'] = tenant_network['subnets'][0]
    return params
