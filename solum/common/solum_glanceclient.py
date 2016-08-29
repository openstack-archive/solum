# Copyright 2015 - Rackspace Hosting.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from oslo_log import log as logging

from solum.common import clients

LOG = logging.getLogger(__name__)


class GlanceClient(object):
    """Glance client wrapper so we can encapsulate logic in one place."""

    def __init__(self, context):
        self.context = context

    def _get_glance_client(self):
        # Create a new non-cached glance client/connection
        return clients.OpenStackClients(self.context).glance()

    def delete_image_by_name(self, image_name):
        try:
            glance = self._get_glance_client()
            imgs = glance.images.list()
            for i in imgs:
                if i.name == image_name:
                    glance.images.delete(i.id)
        except Exception as e:
            LOG.exception(e)

    def delete_image_by_id(self, image_id):
        try:
            self._get_glance_client().images.delete(image_id)
        except Exception as e:
            LOG.exception(e)
