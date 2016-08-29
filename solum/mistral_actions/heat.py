# Copyright 2014 - Rackspace Hosting.
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

from mistral.actions import std_actions
from mistral import exceptions
from oslo_log import log as logging

LOG = logging.getLogger('mistral.actions.solum')


class UpdateStackAction(std_actions.HTTPAction):
    def __init__(self, heat_service_url, action_context,
                 stack_name, stack_id, parameters, image_id, template):
        merged_parms = parameters or {}
        merged_parms['image'] = image_id
        super(UpdateStackAction, self).__init__(
            url='%s/stacks/%s/%s' % (heat_service_url, stack_name, stack_id),
            method='PUT',
            headers={'X-Auth-Token': action_context['openstack']['auth_token'],
                     'Content-Type': 'application/json',
                     'User-Agent': 'mistral-heat-plugin',
                     'Accept': 'application/json'},
            body={'stack_id': stack_id,
                  'parameters': merged_parms,
                  'template': template},
            timeout=30)

    def is_sync(self):
        return True


class CheckStackAction(std_actions.HTTPAction):
    def __init__(self, heat_service_url, action_context,
                 stack_name, stack_id):
        super(CheckStackAction, self).__init__(
            url='%s/stacks/%s/%s' % (heat_service_url, stack_name, stack_id),
            method='GET',
            headers={'X-Auth-Token': action_context['openstack']['auth_token'],
                     'Content-Type': 'application/json',
                     'User-Agent': 'mistral-heat-plugin',
                     'Accept': 'application/json'})

    def run(self):
        resp = super(CheckStackAction, self).run()
        LOG.debug('CheckStackAction resp:%s' % resp['content'].get('stack'))
        if resp['content']['stack']['stack_status'] != 'UPDATE_COMPLETE':
            raise exceptions.ActionException(
                'Stack update not complete: stack %(stack_name)s/%(id)s,'
                ' status %(stack_status)s' % resp['content']['stack'])
        return {'stack_status': resp['content']['stack']['stack_status']}

    def test(self):
        return {'stack_status': 'UPDATE_COMPLETE'}

    def is_sync(self):
        return True
