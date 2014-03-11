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

import os.path
import subprocess
import uuid

from solum.api.handlers import handler
from solum import objects
from solum.openstack.common import log as logging

LOG = logging.getLogger(__name__)


STATES = (PENDING, BUILDING, ERROR, COMPLETE) = (
    'PENDING', 'BUILDING', 'ERROR', 'COMPLETE')


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
        db_obj.state = PENDING
        db_obj.create(self.context)
        self._start_build(db_obj)
        return db_obj

    def _start_build(self, image):
        # we could do this with the docker/git python client.

        proj_dir = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                '..', '..', '..'))
        build_app = os.path.join(proj_dir, 'contrib',
                                 'lp-cedarish', 'docker', 'build-app')
        image.state = BUILDING
        image.save(self.context)
        try:
            out = subprocess.Popen([build_app, image.source_uri,
                                    image.name],
                                   stdout=subprocess.PIPE).communicate()[0]
        except subprocess.CalledProcessError as subex:
            LOG.exception(subex)
            image.state = ERROR
            image.save(self.context)
            return
        LOG.debug(out)
        image.state = COMPLETE
        image.save(self.context)
