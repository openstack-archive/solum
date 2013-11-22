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
from wsme import types as wtypes
import wsmeext.pecan as wsme_pecan

from solum.api.controllers import common_types


class Assembly(wtypes.Base):
    """Representation of an Assembly.

    The Assembly resource represents a group of components that make
    up a running instance of an application. You may casually refer
    to this as "the application" but we refer to it as an Assembly because
    most cloud applications are actually a system of multiple service
    instances that make up a system. For example, a three-tier web application
    may have a load balancer component, a group of application servers, and a
    database server all represented as Component resources that make up an
    Assembly resource. An Assembly resource has at least one Component resource
    associated with it.
    """

    uri = common_types.Uri
    "Uri to the Assembly"

    name = wtypes.text
    "Name of the Assembly"

    description = wtypes.text
    "Description of the Assembly"

    @classmethod
    def sample(cls):
        return cls(uri='http://localhost/v1/assemblies/x4',
                   name='database',
                   description='A mysql database')


class AssemblyController(rest.RestController):
    """Manages operations on a single assembly."""

    def __init__(self, assembly_id):
        pecan.request.context['assembly_id'] = assembly_id
        self._id = assembly_id

    @wsme_pecan.wsexpose(Assembly, wtypes.text)
    def get(self):
        """Return this assembly."""
        error = _("Not implemented")
        pecan.response.translatable_error = error
        raise wsme.exc.ClientSideError(unicode(error))

    @wsme_pecan.wsexpose(Assembly, wtypes.text, body=Assembly)
    def put(self, data):
        """Modify this assembly."""
        error = _("Not implemented")
        pecan.response.translatable_error = error
        raise wsme.exc.ClientSideError(unicode(error))

    @wsme_pecan.wsexpose(None, wtypes.text, status_code=204)
    def delete(self):
        """Delete this assembly."""
        error = _("Not implemented")
        pecan.response.translatable_error = error
        raise wsme.exc.ClientSideError(unicode(error))


class AssembliesController(rest.RestController):
    """Manages operations on the assemblies collection."""

    @pecan.expose()
    def _lookup(self, assembly_id, *remainder):
        if remainder and not remainder[-1]:
            remainder = remainder[:-1]
        return AssemblyController(assembly_id), remainder

    @wsme_pecan.wsexpose(Assembly, body=Assembly, status_code=201)
    def post(self, data):
        """Create a new assembly."""
        error = _("Not implemented")
        pecan.response.translatable_error = error
        raise wsme.exc.ClientSideError(unicode(error))

    @wsme_pecan.wsexpose([Assembly])
    def get_all(self):
        """Return all assemblys, based on the query provided."""
        return []
