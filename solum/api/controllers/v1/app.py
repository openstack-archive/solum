# Copyright 2015 - Rackspace US, Inc.
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

import json
import re

from oslo_config import cfg
from oslo_log import log as logging
import pecan
from pecan import rest
import wsmeext.pecan as wsme_pecan

from solum.api.controllers.v1.datamodel import app
from solum.api.controllers.v1 import workflow
from solum.api.handlers import app_handler
from solum.common import exception
from solum.common import request
from solum.common import yamlutils
from solum import objects

LOG = logging.getLogger(__name__)


class AppController(rest.RestController):
    """Manages operations on a single app."""

    def __init__(self, app_id):
        super(AppController, self).__init__()
        self._id = app_id

    @exception.wrap_wsme_pecan_controller_exception
    @pecan.expose()
    def _lookup(self, resource, *remainder):
        if remainder and not remainder[-1]:
            remainder = remainder[:-1]
        if resource == 'workflows':
            return workflow.WorkflowsController(self._id), remainder

    @exception.wrap_wsme_pecan_controller_exception
    @wsme_pecan.wsexpose(app.App)
    def get(self):
        """Return this app."""
        request.check_request_for_https()
        handler = app_handler.AppHandler(pecan.request.security_context)
        app_model = handler.get(self._id)
        host_url = pecan.request.application_url.rstrip('/')
        app_model = app.App.from_db_model(app_model, host_url)
        return app_model

    @exception.wrap_wsme_pecan_controller_exception
    @wsme_pecan.wsexpose(app.App, body=app.App, status_code=200)
    def patch(self, data):
        """Modify this app."""
        request.check_request_for_https()
        handler = app_handler.AppHandler(pecan.request.security_context)
        handler.get(self._id)

        if not data:
            raise exception.BadRequest(reason="No body detected")

        updated_app = handler.patch(self._id, data)
        host_url = pecan.request.application_url.rstrip('/')
        updated_app = app.App.from_db_model(updated_app, host_url)

        return updated_app

    @exception.wrap_pecan_controller_exception
    @wsme_pecan.wsexpose(status_code=202)
    def delete(self):
        """Delete this app."""
        handler = app_handler.AppHandler(pecan.request.security_context)
        handler.delete(self._id)


class AppsController(rest.RestController):
    """Manages operations on the apps collection."""

    def _validate(self, app_data):
        # check max apps created for given tenant
        handler = app_handler.AppHandler(pecan.request.security_context)
        if len(handler.get_all()) >= cfg.CONF.api.max_apps_per_tenant:
            msg = "Cannot create application as maximum allowed limit reached."
            raise exception.ResourceLimitExceeded(reason=msg)

        if not app_data.languagepack:
            raise exception.BadRequest(reason="Languagepack not specified.")

        if not app_data.name:
            raise exception.BadRequest(reason='App name cannot be empty.')

        msg = ("Application name must be 1-100 characters long, only contain "
               "a-z,0-9,-,_ and start with an alphabet character.")
        # check if app name contains any invalid characters
        if not app_data.name or not app_data.name[0].isalpha():
            raise exception.BadRequest(reason=msg)

        try:
            re.match(r'^([a-z0-9-_]{1,100})$', app_data.name).group(0)
        except AttributeError:
            raise exception.BadRequest(reason=msg)

        msg = "Application description must be less than 255 characters."
        if app_data.description and len(app_data.description) > 255:
            raise exception.BadRequest(reason=msg)

        # check if languagepack exists or not
        if str(app_data.languagepack).lower() != "false":
            try:
                objects.registry.Image.get_lp_by_name_or_uuid(
                    pecan.request.security_context,
                    app_data.languagepack,
                    include_operators_lp=True)
            except exception.ResourceNotFound:
                raise exception.ObjectNotFound(name="Languagepack",
                                               id=app_data.languagepack)

    @pecan.expose()
    def _lookup(self, app_id, *remainder):
        if remainder and not remainder[-1]:
            remainder = remainder[:-1]
        return AppController(app_id), remainder

    @exception.wrap_pecan_controller_exception
    @wsme_pecan.wsexpose(app.App, body=app.App, status_code=201)
    def post(self, data):
        """Create a new app."""
        request.check_request_for_https()
        if not data:
            raise exception.BadRequest(reason='No data.')

        self._validate(data)

        handler = app_handler.AppHandler(pecan.request.security_context)

        app_data = data.as_dict(app.App)

        try:
            raw_content = yamlutils.load(pecan.request.body)
        except ValueError:
            try:
                raw_content = json.loads(pecan.request.body)
            except ValueError as exp:
                LOG.exception(exp)
                raise exception.BadRequest(reason='Invalid app data.')

        app_data['raw_content'] = json.dumps(raw_content)

        new_app = handler.create(app_data)
        host_url = pecan.request.application_url.rstrip('/')
        created_app = app.App.from_db_model(new_app, host_url)
        return created_app

    @exception.wrap_wsme_pecan_controller_exception
    @wsme_pecan.wsexpose([app.App])
    def get_all(self):
        """Return all apps, based on the query provided."""
        request.check_request_for_https()
        handler = app_handler.AppHandler(pecan.request.security_context)
        host_url = pecan.request.application_url.rstrip('/')
        all_apps = [app.App.from_db_model(obj, host_url)
                    for obj in handler.get_all()]
        return all_apps
