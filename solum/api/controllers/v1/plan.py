# Copyright 2013 - Rackspace US, Inc.
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
import sys

from oslo.db import exception as db_exc
import pecan
from pecan import rest
from wsme.rest import json as wsme_json
from wsme import types as wsme_types
import wsmeext.pecan as wsme_pecan

from solum.api.controllers.v1.datamodel import plan
from solum.api.handlers import plan_handler
from solum.common import exception
from solum.common import yamlutils
from solum import objects


def init_plan_v1(input_plan):
    plan_handler_v1 = plan_handler.PlanHandler(
        pecan.request.security_context)
    plan_v1 = plan.Plan(**input_plan)
    return plan_handler_v1, plan_v1


def init_plan_by_version(input_plan):
    version = input_plan.get('version')
    if version is None:
        raise exception.BadRequest(
            reason='Version attribute is missing in Plan')
    mod = sys.modules[__name__]
    if not hasattr(mod, 'init_plan_v%s' % version):
        raise exception.BadRequest(reason='Plan version %s is invalid.'
                                          % version)
    return getattr(mod, 'init_plan_v%s' % version)(input_plan)


def init_yml_plan_by_version():
    try:
        yml_input_plan = yamlutils.load(pecan.request.body)
    except ValueError as excp:
        raise exception.BadRequest(reason='Plan is invalid. '
                                          + excp.message)
    return init_plan_by_version(yml_input_plan)


def init_json_plan_by_version():
    try:
        json_input_plan = json.loads(pecan.request.body)
    except ValueError as excp:
        raise exception.BadRequest(reason='Plan is invalid. '
                                          + excp.message)
    return init_plan_by_version(json_input_plan)


def yaml_content(m):
    ref_content = m.refined_content()
    ref_content['uri'] = '%s/v1/plans/%s' % (pecan.request.host_url,
                                             m.uuid)
    return ref_content


class PlanController(rest.RestController):
    """Manages operations on a single plan."""

    def __init__(self, plan_id):
        super(PlanController, self).__init__()
        self._id = plan_id

    @exception.wrap_pecan_controller_exception
    @pecan.expose()
    def get(self):
        """Return this plan."""
        handler = plan_handler.PlanHandler(pecan.request.security_context)

        if pecan.request.accept is not None and 'yaml' in pecan.request.accept:
            plan_serialized = yamlutils.dump(
                yaml_content(handler.get(self._id)))
        else:
            plan_model = plan.Plan.from_db_model(
                handler.get(self._id), pecan.request.host_url)
            plan_serialized = wsme_json.encode_result(plan_model, plan.Plan)
        pecan.response.status = 200
        return plan_serialized

    @exception.wrap_pecan_controller_exception
    @pecan.expose(content_type='application/x-yaml')
    def put(self):
        """Modify this plan."""
        if not pecan.request.body or len(pecan.request.body) < 1:
            raise exception.BadRequest
        try:
            yml_input_plan = yamlutils.load(pecan.request.body)
        except ValueError as excp:
            raise exception.BadRequest(reason='Plan is invalid. '
                                              + excp.message)
        handler, data = init_plan_by_version(yml_input_plan)
        updated_plan_yml = yamlutils.dump(yaml_content(handler.update(
            self._id, data.as_dict(objects.registry.Plan))))
        pecan.response.status = 200
        return updated_plan_yml

    @exception.wrap_wsme_controller_exception
    @wsme_pecan.wsexpose(status_code=204)
    def delete(self):
        """Delete this plan."""
        handler = plan_handler.PlanHandler(pecan.request.security_context)
        try:
            handler.delete(self._id)
        except db_exc.DBReferenceError:
            raise exception.PlanStillReferenced(name=self._id)
        except db_exc.DBError as dbe:
            raise exception.SolumException(reason=dbe.message)


class PlansController(rest.RestController):
    """Manages operations on the plans collection."""

    @pecan.expose()
    def _lookup(self, plan_id, *remainder):
        if remainder and not remainder[-1]:
            remainder = remainder[:-1]
        return PlanController(plan_id), remainder

    @exception.wrap_pecan_controller_exception
    @pecan.expose()
    def post(self):
        """Create a new plan."""
        if not pecan.request.body or len(pecan.request.body) < 1:
                raise exception.BadRequest
        if (pecan.request.content_type is not None and
                'yaml' in pecan.request.content_type):
            handler, data = init_yml_plan_by_version()
            created_plan = yamlutils.dump(yaml_content(handler.create(
                data.as_dict(objects.registry.Plan))))
        else:
            handler, data = init_json_plan_by_version()
            plan_wsme = plan.Plan.from_db_model(handler.create(
                data.as_dict(objects.registry.Plan)), pecan.request.host_url)
            created_plan = wsme_json.encode_result(plan_wsme, plan.Plan)
        pecan.response.status = 201
        return created_plan

    @exception.wrap_pecan_controller_exception
    @pecan.expose()
    def get_all(self):
        """Return all plans, based on the query provided."""
        handler = plan_handler.PlanHandler(pecan.request.security_context)

        if pecan.request.accept is not None and 'yaml' in pecan.request.accept:
            plan_serialized = yamlutils.dump([yaml_content(obj)
                                              for obj in handler.get_all()
                                              if obj and obj.raw_content])
        else:
            plan_serialized = wsme_json.encode_result(
                [plan.Plan.from_db_model(obj, pecan.request.host_url)
                 for obj in handler.get_all()],
                wsme_types.ArrayType(plan.Plan))
        pecan.response.status = 200
        return plan_serialized
