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

import pecan
from pecan import rest
from urllib import parse
from wsme.rest import json as wsme_json
from wsme import types as wsme_types
import wsmeext.pecan as wsme_pecan

from solum.api.controllers.camp.v1_1.datamodel import assemblies as model
from solum.api.controllers.camp.v1_1 import uris
from solum.api.controllers import common_types
from solum.api.handlers.camp import assembly_handler
from solum.api.handlers.camp import plan_handler
from solum.common import exception


class AssembliesController(rest.RestController):
    """CAMP v1.1 assemblies controller."""

    @exception.wrap_wsme_controller_exception
    @wsme_pecan.wsexpose(None, wsme_types.text, status_code=204)
    def delete(self, uuid):
        """Delete this assembly."""
        handler = assembly_handler.AssemblyHandler(
            pecan.request.security_context)
        handler.delete(uuid)

    @exception.wrap_wsme_controller_exception
    @wsme_pecan.wsexpose(model.Assemblies)
    def get(self):
        host_url = pecan.request.application_url.rstrip('/')
        auri = uris.ASSEMS_URI_STR % host_url
        pdef_uri = uris.DEPLOY_PARAMS_URI % host_url
        desc = "Solum CAMP API assemblies collection resource"

        handler = (assembly_handler.
                   AssemblyHandler(pecan.request.security_context))
        asem_objs = handler.get_all()
        a_links = []
        for m in asem_objs:
            a_links.append(common_types.Link(href=uris.ASSEM_URI_STR %
                                             (host_url, m.uuid),
                                             target_name=m.name))

        # if there aren't any assemblies, avoid returning a resource with an
        # empty assembly_links array
        if len(a_links) > 0:
            res = model.Assemblies(uri=auri,
                                   name='Solum_CAMP_assemblies',
                                   type='assemblies',
                                   description=desc,
                                   parameter_definitions_uri=pdef_uri,
                                   assembly_links=a_links)
        else:
            res = model.Assemblies(uri=auri,
                                   name='Solum_CAMP_assemblies',
                                   type='assemblies',
                                   description=desc,
                                   parameter_definitions_uri=pdef_uri)

        return res

    @exception.wrap_wsme_controller_exception
    @wsme_pecan.wsexpose(model.Assembly, wsme_types.text)
    def get_one(self, uuid):
        """Return the appropriate CAMP-style assembly resource."""
        host_url = pecan.request.application_url.rstrip('/')
        handler = assembly_handler.AssemblyHandler(
            pecan.request.security_context)
        return model.Assembly.from_db_model(handler.get(uuid),
                                            host_url)

    @exception.wrap_pecan_controller_exception
    @pecan.expose('json', content_type='application/json')
    def post(self):
        """Create a new application.

        There are a number of ways to use this method to create a new
        application. See Section 6.11 of the CAMP v1.1 specification
        for an explanation of each. Use the Content-Type of request to
        determine what the client is trying to do.
        """
        if pecan.request.content_type is None:
            raise exception.UnsupportedMediaType(
                name=pecan.request.content_type,
                method='POST')

        req_content_type = pecan.request.content_type
        host_url = pecan.request.application_url.rstrip('/')

        # deploying by reference uses a JSON payload
        if req_content_type == 'application/json':
            payload = pecan.request.body
            if not payload or len(payload) < 1:
                raise exception.BadRequest(reason='empty request body')

            try:
                json_ref_doc = json.loads(payload)
            except ValueError as excp:
                raise exception.BadRequest(reason='JSON object is invalid. '
                                           + str(excp))

            if 'plan_uri' in json_ref_doc:
                plan_uri_str = json_ref_doc['plan_uri']

                # figure out if the plan uri is relative or absolute
                plan_uri = parse.urlparse(plan_uri_str)
                uri_path = plan_uri.path
                if not plan_uri.netloc:
                    # should be something like "../plans/<uuid>" or
                    # "/camp/v1_1/plans/<uuid> (include Solum plans)
                    if (not uri_path.startswith('../plans/') and
                            not uri_path.startswith('../../../v1/plans/') and
                            not uri_path.startswith('/camp/v1_1/plans/') and
                            not uri_path.startswith('/v1/plans/')):
                        msg = 'plan_uri does not reference a plan resource'
                        raise exception.BadRequest(reason=msg)

                    plan_uuid = plan_uri.path.split('/')[-1]

                else:
                    # We have an absolute URI. Try to figure out if it refers
                    # to a plan on this Solum instance. Note the following code
                    # does not support URI aliases. A request that contains
                    # a 'plan_uri' with a network location that is different
                    # than network location used to make this request but
                    # which, nevertheless, still refers to this Solum instance
                    # will experience a false negative. This code will treat
                    # that plan as if it existed on another CAMP-compliant
                    # server.
                    if plan_uri_str.startswith(host_url):
                        if (not uri_path.startswith('/camp/v1_1/plans/') and
                                not uri_path.startswith('/v1/plans/')):
                            msg = 'plan_uri does not reference a plan resource'
                            raise exception.BadRequest(reason=msg)

                        plan_uuid = plan_uri.path.split('/')[-1]

                    else:
                        # The plan exists on another server.
                        # TODO(gpilz): support references to plans on other
                        # servers
                        raise exception.NotImplemented()

                # resolve the local plan by its uuid. this will raise a
                # ResourceNotFound exception if there is no plan with
                # this uuid
                phandler = plan_handler.PlanHandler(
                    pecan.request.security_context)
                plan_obj = phandler.get(plan_uuid)

            elif 'pdp_uri' in json_ref_doc:
                # TODO(gpilz): support references to PDPs
                raise exception.NotImplemented()
            else:
                # must have either 'plan_uri' or 'pdp_uri'
                msg = 'JSON object must contain either plan_uri or pdp_uri'
                raise exception.BadRequest(reason=msg)
        else:
            # TODO(gpilz): support deploying an application by value
            raise exception.NotImplemented()

        # at this point we expect to have a reference to a plan database object
        # for the plan that will be used to create the application
        ahandler = assembly_handler.AssemblyHandler(
            pecan.request.security_context)
        assem_db_obj = ahandler.create_from_plan(plan_obj)
        assem_model = model.Assembly.from_db_model(assem_db_obj, host_url)

        pecan.response.status = 201
        pecan.response.location = assem_model.uri
        return wsme_json.tojson(model.Assembly, assem_model)
