# Copyright 2014 - Rackspace Hosting
#
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

import uuid

from solum.api.handlers import handler
from solum import objects
from solum.openstack.common import log as logging
from solum.worker import api

LOG = logging.getLogger(__name__)


class ImageHandler(handler.Handler):
    """Fulfills a request on the image resource."""

    def get(self, id):
        """Return an image."""
        return objects.registry.Image.get_by_uuid(self.context, id)

    def create(self, data):
        """Create a new resource."""
        db_obj = objects.registry.Image()
        db_obj.uuid = str(uuid.uuid4())
        db_obj.user_id = self.context.user
        db_obj.project_id = self.context.tenant
        db_obj.name = data.get('name')
        db_obj.source_uri = data.get('source_uri')
        db_obj.tags = data.get('tags')
        db_obj.state = api.PENDING
        db_obj.create(self.context)
        self._start_build(db_obj)
        return db_obj

    def _start_build(self, image):
        api.API(context=self.context).build(
            build_id=image.id,
            source_uri=image.source_uri,
            name=image.name,
            base_image_id=image.base_image_id,
            source_format=image.source_format,
            image_format=image.image_format)
