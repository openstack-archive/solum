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

import pecan
from pecan import rest
from wsme.rest import json as wjson
from wsme import types as wtypes
import wsmeext.pecan as wsme_pecan

from solum.api.controllers.v1.datamodel import types as api_types
from solum.builder.handlers import image_handler
from solum.common import exception

STATE_KIND = wtypes.Enum(str, 'BUILDING', 'ERROR', 'COMPLETE')


class Image(api_types.Base):
    """The Image resource represents an image."""

    source_uri = wtypes.text
    """The URI of the app/element."""

    state = STATE_KIND
    """The state of the image. """

    @classmethod
    def sample(cls):
        return cls(uri='http://example.com/v1/images/b3e0d79',
                   source_uri='git://example.com/project/app.git',
                   name='php-web-app',
                   type='image',
                   description='A php web application',
                   tags=['group_xyz'],
                   project_id='1dae5a09ef2b4d8cbf3594b0eb4f6b94',
                   user_id='55f41cf46df74320b9486a35f5d28a11')

    @classmethod
    def from_db_object(cls, obj, host_url):
        jplan = {}
        jplan['type'] = 'image'
        jplan['uri'] = '%s/images/%s' % (host_url, obj.uuid)
        jplan['user_id'] = obj.user_id
        jplan['project_id'] = obj.project_id
        jplan['source_uri'] = obj.source_uri
        jplan['name'] = obj.name
        jplan['description'] = obj.description
        return cls(**jplan)

    def as_dict(self):
        return wjson.tojson(Image, self)


class ImageController(rest.RestController):
    """Manages operations on a single image."""

    def __init__(self, image_id):
        self._id = image_id

    @exception.wrap_controller_exception
    @wsme_pecan.wsexpose(Image)
    def get(self):
        """Return this image."""
        handler = image_handler.ImageHandler()
        host_url = pecan.request.host_url
        return Image.from_db_object(handler.get(self._id), host_url)


class ImagesController(rest.RestController):
    """Manages operations on the images collection."""

    @pecan.expose()
    def _lookup(self, image_id, *remainder):
        if remainder and not remainder[-1]:
            remainder = remainder[:-1]
        return ImageController(image_id), remainder

    @wsme_pecan.wsexpose(Image, body=Image, status_code=201)
    def post(self, data):
        """Create a new image."""
        handler = image_handler.ImageHandler()
        host_url = pecan.request.host_url
        return Image.from_db_object(
            handler.create(data.as_dict()), host_url)
