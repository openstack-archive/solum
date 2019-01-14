# Copyright 2013 - Red Hat, Inc.
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
import wsme
import wsmeext.pecan as wsme_pecan

from solum.api.controllers.v1.datamodel import assembly
import solum.api.controllers.v1.userlog as userlog_controller
from solum.api.handlers import assembly_handler
from solum.common import exception
from solum.common import policy
from solum.common import request
from solum.i18n import _
from solum import objects


class AssemblyController(rest.RestController):
    """Manages operations on a single assembly."""

    def __init__(self, assembly_id):
        super(AssemblyController, self).__init__()
        self._id = assembly_id

    @pecan.expose()
    def _lookup(self, primary_key, *remainder):
        if remainder and not remainder[-1]:
            remainder = remainder[:-1]
        if primary_key == 'logs':
            logs = userlog_controller.UserlogsController(self._id)
            return logs, remainder

    @exception.wrap_wsme_pecan_controller_exception
    @wsme_pecan.wsexpose(assembly.Assembly)
    def get(self):
        """Return this assembly."""
        policy.check('show_assembly',
                     pecan.request.security_context)
        request.check_request_for_https()
        handler = assembly_handler.AssemblyHandler(
            pecan.request.security_context)
        host_url = pecan.request.application_url.rstrip('/')
        return assembly.Assembly.from_db_model(handler.get(self._id), host_url)

    @exception.wrap_wsme_pecan_controller_exception
    @wsme_pecan.wsexpose(assembly.Assembly, body=assembly.Assembly)
    def put(self, data):
        """Modify this assembly."""
        policy.check('update_assembly',
                     pecan.request.security_context)
        handler = assembly_handler.AssemblyHandler(
            pecan.request.security_context)
        res = handler.update(self._id,
                             data.as_dict(objects.registry.Assembly))
        host_url = pecan.request.application_url.rstrip('/')
        return assembly.Assembly.from_db_model(res, host_url)

    @exception.wrap_wsme_pecan_controller_exception
    @wsme_pecan.wsexpose(status_code=204)
    def delete(self):
        """Delete this assembly."""
        policy.check('delete_assembly',
                     pecan.request.security_context)
        handler = assembly_handler.AssemblyHandler(
            pecan.request.security_context)
        return handler.delete(self._id)


class AssembliesController(rest.RestController):
    """Manages operations on the assemblies collection."""

    @pecan.expose()
    def _lookup(self, assembly_id, *remainder):
        if remainder and not remainder[-1]:
            remainder = remainder[:-1]
        return AssemblyController(assembly_id), remainder

    @exception.wrap_wsme_pecan_controller_exception
    @wsme_pecan.wsexpose(assembly.Assembly, body=assembly.Assembly,
                         status_code=201)
    def post(self, data):
        """Create a new assembly."""
        policy.check('create_assembly', pecan.request.security_context)
        host_url = pecan.request.application_url.rstrip('/')
        js_data = data.as_dict(objects.registry.Assembly)
        if data.plan_uri is not wsme.Unset:
            plan_uri = data.plan_uri
            if plan_uri.startswith(host_url):
                pl_uuid = plan_uri.split('/')[-1]
                pl = objects.registry.Plan.get_by_uuid(
                    pecan.request.security_context, pl_uuid)
                js_data['plan_id'] = pl.id
            else:
                # TODO(asalkeld) we are not hosting the plan so
                # download the plan and insert it into our db.
                raise exception.BadRequest(reason=_(
                    'The plan was not hosted in solum'))

        if js_data.get('plan_id') is None:
            raise exception.BadRequest(reason=_(
                'The plan was not given or could not be found'))

        handler = assembly_handler.AssemblyHandler(
            pecan.request.security_context)
        return assembly.Assembly.from_db_model(
            handler.create(js_data), host_url)

    @exception.wrap_wsme_pecan_controller_exception
    @wsme_pecan.wsexpose([assembly.Assembly])
    def get_all(self):
        """Return all assemblies, based on the query provided."""
        policy.check('get_assemblies',
                     pecan.request.security_context)
        request.check_request_for_https()
        handler = assembly_handler.AssemblyHandler(
            pecan.request.security_context)
        host_url = pecan.request.application_url.rstrip('/')
        return [assembly.Assembly.from_db_model(assm, host_url)
                for assm in handler.get_all()]
