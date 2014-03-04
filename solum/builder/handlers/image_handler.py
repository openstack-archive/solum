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


class ImageHandler(handler.Handler):
    """Fulfills a request on the image resource."""

    def get(self, id):
        """Return an image."""
        return objects.registry.Image.get_by_uuid(None, id)

    def create(self, data):
        """Create a new resource."""
        db_obj = objects.registry.Image()
        db_obj.uuid = str(uuid.uuid4())
        db_obj.user_id = data.get('user_id')
        db_obj.project_id = data.get('project_id')
        db_obj.name = data.get('name')
        db_obj.source_uri = data.get('source_uri')
        db_obj.tags = data.get('tags')
        db_obj.create(None)
        return db_obj
