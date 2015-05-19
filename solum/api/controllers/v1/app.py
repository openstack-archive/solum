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

import pecan
from pecan import rest
import wsmeext.pecan as wsme_pecan

from solum.api.controllers.v1.datamodel import app
from solum.api.handlers import app_handler
from solum.common import exception
from solum.common import request
from solum.openstack.common import log as logging

LOG = logging.getLogger(__name__)


class AppController(rest.RestController):
    """Manages operations on a single app."""

    def __init__(self, app_id):
        super(AppController, self).__init__()
        self._id = app_id

    @exception.wrap_pecan_controller_exception
    @wsme_pecan.wsexpose(app.App)
    def get(self):
        """Return this app."""
        request.check_request_for_https()
        handler = app_handler.AppHandler(pecan.request.security_context)
        app_model = handler.get(self._id)
        app_model = app.App.from_db_model(app_model,
                                          pecan.request.host_url)
        return app_model

    @exception.wrap_pecan_controller_exception
    @wsme_pecan.wsexpose(app.App, body=app.App, status_code=200)
    def patch(self, data):
        """Modify this app."""
        request.check_request_for_https()
        handler = app_handler.AppHandler(pecan.request.security_context)
        handler.get(self._id)

        if not data:
            raise exception.BadRequest(reason="No body detected")

        updated_app = handler.patch(self._id, data)
        updated_app = app.App.from_db_model(updated_app,
                                            pecan.request.host_url)

        return updated_app

    @exception.wrap_wsme_controller_exception
    @wsme_pecan.wsexpose(status_code=202)
    def delete(self):
        """Delete this app."""
        handler = app_handler.AppHandler(pecan.request.security_context)
        handler.delete(self._id)


class AppsController(rest.RestController):
    """Manages operations on the apps collection."""

    @pecan.expose()
    def _lookup(self, app_id, *remainder):
        if remainder and not remainder[-1]:
            remainder = remainder[:-1]
        return AppController(app_id), remainder

    @exception.wrap_pecan_controller_exception
    @wsme_pecan.wsexpose(app.App, body=app.App, status_code=200)
    def post(self, data):
        """Create a new app."""
        request.check_request_for_https()
        if not data:
            raise exception.BadRequest(reason='No data.')

        handler = app_handler.AppHandler(pecan.request.security_context)

        app_data = data.as_dict(app.App)
        new_app = handler.create(app_data)
        created_app = app.App.from_db_model(new_app, pecan.request.host_url)
        return created_app

    @exception.wrap_pecan_controller_exception
    @wsme_pecan.wsexpose([app.App])
    def get_all(self):
        """Return all apps, based on the query provided."""
        request.check_request_for_https()
        handler = app_handler.AppHandler(pecan.request.security_context)
        all_apps = [app.App.from_db_model(obj, pecan.request.host_url)
                    for obj in handler.get_all()]
        return all_apps
