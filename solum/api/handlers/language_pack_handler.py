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

from oslo_config import cfg
from oslo_log import log as logging
from oslo_utils import uuidutils
from swiftclient import exceptions as swiftexp

from solum.api.handlers import common
from solum.api.handlers import handler
from solum.api.handlers import userlog_handler
from solum.common import exception as exc
from solum.common import solum_glanceclient
from solum.common import solum_swiftclient
from solum import objects
from solum.objects import image
from solum.objects.sqlalchemy import app
from solum.worker import api


LOG = logging.getLogger(__name__)

# Register options for the service
API_SERVICE_OPTS = [
    cfg.StrOpt('operator_project_id',
               default='',
               help='Tenant id of the operator account used to create LPs'),
    cfg.IntOpt('max_languagepack_limit',
               default=10,
               help='Maximum number of languagepacks allowed'),
]


def list_opts():
    yield 'api', API_SERVICE_OPTS


CONF = cfg.CONF
CONF.register_opts(API_SERVICE_OPTS, group='api')
cfg.CONF.import_opt('image_storage', 'solum.worker.config', group='worker')


class LanguagePackHandler(handler.Handler):
    """Fulfills a request on the languagepack resource."""

    def _check_lp_referenced_in_any_plan(self, ctxt, db_obj):
        plans = objects.registry.PlanList.get_all(ctxt)
        for plan in plans:
            # (devkulkarni): Adding check for raw_contents because
            # there are 'plans' in our db that don't have the
            # raw_contents field. These plans correspond to the
            # 'dummy' plans that we are creating corresponding
            # to 'app deploy' requests.
            if hasattr(plan, 'raw_content') and plan.raw_content:
                if plan.raw_content and 'artifacts' in plan.raw_content:
                    for artifact in plan.raw_content['artifacts']:
                        lp = artifact.get('language_pack', '')
                        if lp == db_obj.name or lp == db_obj.uuid:
                            return True

    def _check_lp_referenced_in_any_app(self, ctxt, db_obj):
        apps = app.App.get_all_by_lp(ctxt, db_obj.name)
        if len(apps) > 0:
            return True
        else:
            apps = app.App.get_all_by_lp(ctxt, db_obj.uuid)
            if len(apps) > 0:
                return True
            else:
                return False

    def _check_if_limit_of_lps_reached(self, ctxt):
        num_of_lps = objects.registry.Image.get_num_of_lps(ctxt)
        if num_of_lps >= int(cfg.CONF.api.max_languagepack_limit):
            msg = "Number of languagepacks reached limit of '%s'." % (
                cfg.CONF.api.max_languagepack_limit)
            raise exc.ResourceLimitExceeded(reason=msg)

    def get(self, id):
        """Return a languagepack."""
        return objects.registry.Image.get_lp_by_name_or_uuid(
            self.context, id, include_operators_lp=True)

    def get_all(self):
        """Return all languagepacks."""
        return objects.registry.Image.get_all_languagepacks(self.context)

    def create(self, data, lp_metadata, lp_params):
        """Create a new languagepack."""

        self._check_if_limit_of_lps_reached(self.context)

        common.check_url(data['source_uri'])

        try:
            # Check if an LP with the same name exists.
            objects.registry.Image.get_lp_by_name_or_uuid(
                self.context, data['name'], include_operators_lp=True)
        except exc.ResourceNotFound:
            db_obj = objects.registry.Image()
            db_obj.update(data)
            db_obj.uuid = uuidutils.generate_uuid()
            db_obj.user_id = self.context.user
            db_obj.project_id = self.context.project_id
            db_obj.status = image.States.QUEUED
            db_obj.artifact_type = 'language_pack'
            if lp_metadata:
                db_obj.tags = []
                db_obj.tags.append(lp_metadata)

            db_obj.create(self.context)
            self._start_build(db_obj, lp_params)
            return db_obj
        else:
            raise exc.ResourceExists(name=data['name'])

    def delete(self, uuid):
        """Delete a languagepack."""
        db_obj = objects.registry.Image.get_lp_by_name_or_uuid(self.context,
                                                               uuid)
        # Check if the languagepack is being used.
        if (self._check_lp_referenced_in_any_plan(self.context, db_obj) or
                self._check_lp_referenced_in_any_app(self.context, db_obj)):
            raise exc.LPStillReferenced(name=uuid)

        if db_obj.docker_image_name:
            img_filename = db_obj.docker_image_name.split('-', 1)[1]

            if cfg.CONF.worker.image_storage == 'swift':
                # Delete image file from swift
                try:
                    swift = solum_swiftclient.SwiftClient(self.context)
                    swift.delete_object('solum_lp', img_filename)
                except swiftexp.ClientException:
                    raise exc.AuthorizationFailure(
                        client='swift',
                        message="Unable to delete languagepack image "
                                "from swift.")
            elif cfg.CONF.worker.image_storage == 'glance':
                glance = solum_glanceclient.GlanceClient(self.context)
                glance.delete_image_by_name(img_filename)
            else:
                LOG.error("Unrecognized image_storage option specified.")
                return

        # Delete logs
        log_handler = userlog_handler.UserlogHandler(self.context)
        log_handler.delete(db_obj.uuid)

        return db_obj.destroy(self.context)

    def _start_build(self, image, lp_params):
        git_info = {
            'source_url': image.source_uri,
        }
        api.API(context=self.context).build_lp(
            image_id=image.id,
            git_info=git_info,
            name=image.name,
            source_format=image.source_format,
            image_format=image.image_format,
            artifact_type=image.artifact_type,
            lp_params=lp_params)
