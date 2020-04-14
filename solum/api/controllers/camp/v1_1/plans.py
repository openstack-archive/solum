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

import jsonpatch
from oslo_db import exception as db_exc
from oslo_utils import uuidutils
import pecan
from pecan import rest
import wsme
from wsme.rest import json as wjson
from wsme import types as wtypes
import wsmeext.pecan as wsme_pecan

from solum.api.controllers.camp.v1_1.datamodel import plans as model
from solum.api.controllers.camp.v1_1 import uris
from solum.api.controllers import common_types
from solum.api.handlers.camp import plan_handler as plan_handler
from solum.common import exception
from solum.common import yamlutils
from solum.i18n import _


MAL_PATCH_ERR = 'JSON Patch request missing one or more required components'
UNSUP_VER_ERR = 'camp_version \'%s\' is not supported by this implementation'


def clean_plan(plan_dict):
    del plan_dict['camp_version']
    return plan_dict


def fluff_plan(plan_dict, pid):
    """Fluff the plan with a camp_version and uri."""
    plan_dict['camp_version'] = "CAMP 1.1"
    host_url = pecan.request.application_url.rstrip('/')
    plan_dict['uri'] = uris.PLAN_URI_STR % (host_url, pid)
    return plan_dict


class JsonPatchProcessingException(exception.SolumException):
    msg_fmt = _("Error while processing the JSON Patch document: %(reason)s")
    code = 500


class PlansController(rest.RestController):
    """CAMP v1.1 plans controller."""

    _custom_actions = {
        'patch': ['PATCH']
    }

    @exception.wrap_wsme_controller_exception
    @wsme_pecan.wsexpose(None, wtypes.text, status_code=204)
    def delete(self, uuid):
        """Delete this plan."""
        handler = (plan_handler.
                   PlanHandler(pecan.request.security_context))
        try:
            handler.delete(uuid)
        except (db_exc.DBReferenceError, db_exc.DBError):
            raise exception.PlanStillReferenced(name=uuid)

    @exception.wrap_wsme_controller_exception
    @wsme_pecan.wsexpose(model.Plan, wtypes.text)
    def get_one(self, uuid):
        """Return the appropriate CAMP-style plan resource."""
        handler = (plan_handler.
                   PlanHandler(pecan.request.security_context))
        db_obj = handler.get(uuid)
        plan_dict = fluff_plan(db_obj.refined_content(), db_obj.uuid)
        return model.Plan(**plan_dict)

    @exception.wrap_wsme_controller_exception
    @wsme_pecan.wsexpose(model.Plans)
    def get(self):
        host_url = pecan.request.application_url.rstrip('/')
        puri = uris.PLANS_URI_STR % host_url
        pdef_uri = uris.DEPLOY_PARAMS_URI % host_url
        desc = "Solum CAMP API plans collection resource."

        handler = plan_handler.PlanHandler(pecan.request.security_context)
        plan_objs = handler.get_all()
        p_links = []
        for m in plan_objs:
            p_links.append(common_types.Link(href=uris.PLAN_URI_STR %
                                             (host_url, m.uuid),
                                             target_name=m.name))

        # if there aren't any plans, avoid returning a resource with an
        # empty plan_links array
        if len(p_links) > 0:
            res = model.Plans(uri=puri,
                              name='Solum_CAMP_plans',
                              type='plans',
                              description=desc,
                              parameter_definitions_uri=pdef_uri,
                              plan_links=p_links)
        else:
            res = model.Plans(uri=puri,
                              name='Solum_CAMP_plans',
                              type='plans',
                              description=desc,
                              parameter_definitions_uri=pdef_uri)
        return res

    @exception.wrap_pecan_controller_exception
    @pecan.expose('json', content_type='application/json-patch+json')
    def patch(self, uuid):
        """Patch an existing CAMP-style plan."""

        handler = (plan_handler.
                   PlanHandler(pecan.request.security_context))
        plan_obj = handler.get(uuid)

        # TODO(gilbert.pilz@oracle.com) check if there are any assemblies that
        # refer to this plan and raise an PlanStillReferenced exception if
        # there are.

        if not pecan.request.body or len(pecan.request.body) < 1:
            raise exception.BadRequest(reason='empty request body')

        # check to make sure the request has the right Content-Type
        if (pecan.request.content_type is None or
                pecan.request.content_type != 'application/json-patch+json'):
            raise exception.UnsupportedMediaType(
                name=pecan.request.content_type,
                method='PATCH')

        try:
            patch = jsonpatch.JsonPatch.from_string(pecan.request.body)
            patched_obj = patch.apply(plan_obj.refined_content())
            db_obj = handler.update(uuid, patched_obj)
        except KeyError:
            # a key error indicates one of the patch operations is missing a
            # component
            raise exception.BadRequest(reason=MAL_PATCH_ERR)
        except jsonpatch.JsonPatchConflict:
            raise exception.Unprocessable
        except jsonpatch.JsonPatchException as jpe:
            raise JsonPatchProcessingException(reason=str(jpe))

        return fluff_plan(db_obj.refined_content(), db_obj.uuid)

    @exception.wrap_pecan_controller_exception
    @pecan.expose('json', content_type='application/x-yaml')
    def post(self):
        """Create a new CAMP-style plan."""
        if not pecan.request.body or len(pecan.request.body) < 1:
            raise exception.BadRequest

        # check to make sure the request has the right Content-Type
        if (pecan.request.content_type is None or
                pecan.request.content_type != 'application/x-yaml'):
            raise exception.UnsupportedMediaType(
                name=pecan.request.content_type,
                method='POST')

        try:
            yaml_input_plan = yamlutils.load(pecan.request.body)
        except ValueError as excp:
            raise exception.BadRequest(reason='Plan is invalid. '
                                       + str(excp))

        camp_version = yaml_input_plan.get('camp_version')
        if camp_version is None:
            raise exception.BadRequest(
                reason='camp_version attribute is missing from submitted Plan')
        elif camp_version != 'CAMP 1.1':
            raise exception.BadRequest(reason=UNSUP_VER_ERR % camp_version)

        # Use Solum's handler as the point of commonality. We can do this
        # because Solum stores plans in the DB in their JSON form.
        handler = (plan_handler.
                   PlanHandler(pecan.request.security_context))
        model_plan = model.Plan(**yaml_input_plan)

        # Move any inline Service Specifications to the "services" section.
        # This avoids an issue where WSME can't properly handle multi-typed
        # attributes (e.g. 'fulfillment'). It also smoothes out the primary
        # difference between CAMP plans and Solum plans, namely that Solum
        # plans don't have inline Service Specifications.
        for art in model_plan.artifacts:
            if art.requirements != wsme.Unset:
                for req in art.requirements:
                    if (req.fulfillment != wsme.Unset and
                        isinstance(req.fulfillment,
                                   model.ServiceSpecification)):
                        s_spec = req.fulfillment

                        # if the inline service spec doesn't have an id
                        # generate one
                        if s_spec.id == wsme.Unset:
                            s_spec.id = uuidutils.generate_uuid()

                        # move the inline service spec to the 'services'
                        # section
                        if model_plan.services == wsme.Unset:
                            model_plan.services = [s_spec]
                        else:
                            model_plan.services.append(s_spec)

                        # set the fulfillment to the service spec id
                        req.fulfillment = "id:%s" % s_spec.id

        db_obj = handler.create(clean_plan(wjson.tojson(model.Plan,
                                                        model_plan)))
        plan_dict = fluff_plan(db_obj.refined_content(), db_obj.uuid)

        pecan.response.status = 201
        pecan.response.location = plan_dict['uri']
        return plan_dict
