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
from oslo_utils import uuidutils


class CreateImageAction(std_actions.HTTPAction):
    def __init__(self, build_service_url, action_context,
                 source_uri, name, base_image_id,
                 source_format, image_format):
        super(CreateImageAction, self).__init__(
            url='%s/v1/images' % build_service_url,
            method='POST',
            headers={'X-Auth-Token': action_context['openstack']['auth_token'],
                     'Content-Type': 'application/json',
                     'User-Agent': 'mistral-solum-plugin',
                     'Accept': 'application/json'},
            body={'name': name,
                  'source_uri': source_uri,
                  'source_format': source_format,
                  'base_image_id': base_image_id,
                  'image_format': image_format,
                  'type': 'image'},
            timeout=30)

    def run(self):
        return super(CreateImageAction, self).run()['content']

    def test(self):
        # This is just an example of what the builder returns.
        return {'created_image_id': '1-2-3-4',
                'state': 'PENDING',
                'uuid': '1-2-34'}

    def is_sync(self):
        return True


class GetImageIdAction(std_actions.HTTPAction):
    def __init__(self, build_service_url, action_context, uuid):
        super(GetImageIdAction, self).__init__(
            url='%s/v1/images/%s' % (build_service_url, uuid),
            method='GET',
            headers={'X-Auth-Token': action_context['openstack']['auth_token'],
                     'Content-Type': 'application/json',
                     'User-Agent': 'mistral-solum-plugin',
                     'Accept': 'application/json'})

    def run(self):
        resp = super(GetImageIdAction, self).run()
        created_image_id = resp['content'].get('created_image_id')
        if not uuidutils.is_uuid_like(created_image_id):
            raise exceptions.ActionException(
                'Image not built yet: image %(created_image_id)s,'
                ' state %(state)s' % resp['content'])
        return resp['content']

    def test(self):
        return {'created_image_id': '1-2-3-4',
                'state': 'PENDING',
                'uuid': '4-3-2-1'}

    def is_sync(self):
        return True
