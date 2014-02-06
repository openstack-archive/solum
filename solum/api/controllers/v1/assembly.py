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
import six
import wsme
from wsme import types as wtypes
import wsmeext.pecan as wsme_pecan

from solum.api.controllers.v1.datamodel import assembly
from solum.api.handlers import assembly_handler as assemblyhandler
from solum.common import exception as solum_exception


class AssemblyController(rest.RestController):
    """Manages operations on a single assembly."""

    def __init__(self, assembly_id):
        pecan.request.context['assembly_id'] = assembly_id
        self._id = assembly_id

    @wsme_pecan.wsexpose(assembly.Assembly, wtypes.text)
    def get(self):
        """Return this assembly."""
        try:
            handler = assemblyhandler.AssemblyHandler()
            return handler.get(self._id)
        except solum_exception.SolumException as excp:
            pecan.response.translatable_error = excp
            raise wsme.exc.ClientSideError(six.text_type(excp), excp.code)

    @wsme_pecan.wsexpose(assembly.Assembly, wtypes.text,
                         body=assembly.Assembly)
    def put(self, data):
        """Modify this assembly."""
        try:
            handler = assemblyhandler.AssemblyHandler()
            return handler.update(self._id, data)
        except solum_exception.SolumException as excp:
            pecan.response.translatable_error = excp
            raise wsme.exc.ClientSideError(six.text_type(excp), excp.code)

    @wsme_pecan.wsexpose(None, wtypes.text, status_code=204)
    def delete(self):
        """Delete this assembly."""
        try:
            handler = assemblyhandler.AssemblyHandler()
            return handler.delete(self._id)
        except solum_exception.SolumException as excp:
            pecan.response.translatable_error = excp
            raise wsme.exc.ClientSideError(six.text_type(excp), excp.code)


class AssembliesController(rest.RestController):
    """Manages operations on the assemblies collection."""

    @pecan.expose()
    def _lookup(self, assembly_id, *remainder):
        if remainder and not remainder[-1]:
            remainder = remainder[:-1]
        return AssemblyController(assembly_id), remainder

    @wsme_pecan.wsexpose(assembly.Assembly, body=assembly.Assembly,
                         status_code=201)
    def post(self, data):
        """Create a new assembly."""
        try:
            handler = assemblyhandler.AssemblyHandler()
            return handler.create(data)
        except solum_exception.SolumException as excp:
            pecan.response.translatable_error = excp
            raise wsme.exc.ClientSideError(six.text_type(excp), excp.code)

    @wsme_pecan.wsexpose([assembly.Assembly])
    def get_all(self):
        """Return all assemblies, based on the query provided."""
        try:
            handler = assemblyhandler.AssemblyHandler()
            return handler.get_all()
        except solum_exception.SolumException as excp:
            pecan.response.translatable_error = excp
            raise wsme.exc.ClientSideError(six.text_type(excp), excp.code)
