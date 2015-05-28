# Copyright 2014 - Rackspace
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

from oslo.config import cfg
from swiftclient import exceptions as swiftexp

from solum.api.handlers import handler
from solum.api.handlers import userlog_handler
from solum.common import exception as exc
from solum.common import solum_swiftclient
from solum import objects
from solum.objects import image
from solum.openstack.common import log as logging
from solum.worker import api

LOG = logging.getLogger(__name__)

# Register options for the service
API_SERVICE_OPTS = [
    cfg.StrOpt('operator_project_id',
               default='',
               help='Tenant id of the operator account used to create LPs'),
]

CONF = cfg.CONF
CONF.register_opts(API_SERVICE_OPTS, group='api')


class LanguagePackHandler(handler.Handler):
    """Fulfills a request on the languagepack resource."""

    def get(self, id):
        """Return a languagepack."""
        return objects.registry.Image.get_lp_by_name_or_uuid(
            self.context, id, include_operators_lp=True)

    def get_all(self):
        """Return all languagepacks."""
        return objects.registry.Image.get_all_languagepacks(self.context)

    def create(self, data, lp_metadata):
        """Create a new languagepack."""
        try:
            # Check if an LP with the same name exists.
            objects.registry.Image.get_lp_by_name_or_uuid(
                self.context, data['name'], include_operators_lp=True)
        except exc.ResourceNotFound:
            db_obj = objects.registry.Image()
            db_obj.update(data)
            db_obj.uuid = str(uuid.uuid4())
            db_obj.user_id = self.context.user
            db_obj.project_id = self.context.tenant
            db_obj.status = image.States.QUEUED
            db_obj.artifact_type = 'language_pack'
            if lp_metadata:
                db_obj.tags = []
                db_obj.tags.append(lp_metadata)

            db_obj.create(self.context)
            self._start_build(db_obj)
            return db_obj
        else:
            raise exc.ResourceExists(name=data['name'])

    def delete(self, uuid):
        """Delete a languagepack."""
        db_obj = objects.registry.Image.get_lp_by_name_or_uuid(self.context,
                                                               uuid)

        # Check if the languagepack is being used.
        plans = objects.registry.PlanList.get_all(self.context)
        for plan in plans:
            lp = plan.raw_content['artifacts'][0]['language_pack']
            if lp == db_obj.name or lp == db_obj.uuid:
                raise exc.LPStillReferenced(name=uuid)

        # Delete image file from swift
        if db_obj.docker_image_name:
            img_filename = db_obj.docker_image_name.split('-', 1)[1]
            try:
                swift = solum_swiftclient.SwiftClient(self.context)
                swift.delete_object('solum_lp', img_filename)
            except swiftexp.ClientException:
                raise exc.AuthorizationFailure(
                    client='swift',
                    message="Unable to delete languagepack image from swift.")

        # Delete logs
        log_handler = userlog_handler.UserlogHandler(self.context)
        log_handler.delete(db_obj.uuid)

        return db_obj.destroy(self.context)

    def _start_build(self, image):
        git_info = {
            'source_url': image.source_uri,
        }
        api.API(context=self.context).build_lp(
            image_id=image.id,
            git_info=git_info,
            name=image.name,
            source_format=image.source_format,
            image_format=image.image_format,
            artifact_type=image.artifact_type)
