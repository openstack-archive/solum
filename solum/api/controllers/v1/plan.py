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
import re
import sys

from oslo_db import exception as db_exc
from oslo_log import log as logging
import pecan
from pecan import rest
from wsme.rest import json as wsme_json
from wsme import types as wsme_types
import wsmeext.pecan as wsme_pecan

from solum.api.controllers.v1.datamodel import plan
from solum.api.handlers import plan_handler
from solum.common import exception
from solum.common import policy
from solum.common import yamlutils
from solum import objects

LOG = logging.getLogger(__name__)


def init_plan_v1(yml_input_plan):
    if not yml_input_plan.get('name'):
        raise exception.BadRequest(reason="Name field is missing.")
    try:
        pp = plan.Plan(**yml_input_plan)
    except ValueError as ve:
        raise exception.BadRequest(reason=str(ve))
    try:
        name_regex = re.compile(r'^([a-zA-Z0-9-_]{1,100})$')
        assert name_regex.match(pp.name), 'Plan name is invalid.'
    except AssertionError as ae:
        raise exception.BadRequest(reason=str(ae))
    return pp


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
        LOG.error("Invalid plan.")
        raise exception.BadRequest(reason='Plan is invalid. '
                                          + str(excp))
    return init_plan_by_version(yml_input_plan)


def init_json_plan_by_version():
    try:
        json_input_plan = json.loads(pecan.request.body)
    except ValueError as excp:
        raise exception.BadRequest(reason='Plan is invalid. '
                                          + str(excp))
    return init_plan_by_version(json_input_plan)


def yaml_content(m):
    ref_content = m.refined_content()
    host_url = pecan.request.application_url.rstrip('/')
    ref_content['uri'] = '%s/v1/plans/%s' % (host_url, m.uuid)
    ref_content['trigger_uri'] = ('%s/v1/triggers/%s' %
                                  (host_url, m.trigger_id))
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
        policy.check('show_plan',
                     pecan.request.security_context)
        handler = plan_handler.PlanHandler(pecan.request.security_context)

        host_url = pecan.request.application_url.rstrip('/')
        if pecan.request.accept is not None and 'yaml' in pecan.request.accept:
            plan_serialized = yamlutils.dump(
                yaml_content(handler.get(self._id)))
        else:
            plan_model = plan.Plan.from_db_model(
                handler.get(self._id), host_url)
            plan_serialized = wsme_json.encode_result(plan_model, plan.Plan)
        pecan.response.status = 200
        return plan_serialized

    @exception.wrap_pecan_controller_exception
    @pecan.expose()
    def put(self):
        """Modify this plan."""
        policy.check('update_plan',
                     pecan.request.security_context)
        # make sure the plan exists before parsing the request
        handler = plan_handler.PlanHandler(pecan.request.security_context)
        handler.get(self._id)

        host_url = pecan.request.application_url.rstrip('/')
        if not pecan.request.body or len(pecan.request.body) < 1:
            raise exception.BadRequest(reason="No data.")

        if (pecan.request.content_type is not None and
                'yaml' in pecan.request.content_type):
            data = init_yml_plan_by_version()
            updated_plan_yml = yamlutils.dump(yaml_content(handler.update(
                self._id, data.as_dict(objects.registry.Plan))))
        else:
            data = init_json_plan_by_version()
            plan_obj = handler.update(self._id,
                                      data.as_dict(objects.registry.Plan))
            updated_plan_yml = wsme_json.encode_result(plan.Plan.from_db_model(
                plan_obj, host_url), plan.Plan)

        pecan.response.status = 200
        return updated_plan_yml

    @exception.wrap_wsme_pecan_controller_exception
    @wsme_pecan.wsexpose(status_code=202)
    def delete(self):
        """Delete this plan."""
        policy.check('delete_plan',
                     pecan.request.security_context)
        p_handler = plan_handler.PlanHandler(pecan.request.security_context)
        try:
            p_handler.delete(self._id)
        except (db_exc.DBError):
            raise exception.PlanStillReferenced(name=self._id)


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
        policy.check('create_plan',
                     pecan.request.security_context)
        if not pecan.request.body or len(pecan.request.body) < 1:
            raise exception.BadRequest(reason="No data.")

        handler = plan_handler.PlanHandler(pecan.request.security_context)

        host_url = pecan.request.application_url.rstrip('/')
        if (pecan.request.content_type is not None and
                'yaml' in pecan.request.content_type):
            data = init_yml_plan_by_version()
            created_plan = yamlutils.dump(yaml_content(handler.create(
                data.as_dict(objects.registry.Plan))))
        else:
            data = init_json_plan_by_version()
            plan_wsme = plan.Plan.from_db_model(handler.create(
                data.as_dict(objects.registry.Plan)), host_url)
            created_plan = wsme_json.encode_result(plan_wsme, plan.Plan)

        pecan.response.status = 201
        return created_plan

    @exception.wrap_pecan_controller_exception
    @pecan.expose()
    def get_all(self):
        """Return all plans, based on the query provided."""
        policy.check('get_plans',
                     pecan.request.security_context)
        handler = plan_handler.PlanHandler(pecan.request.security_context)

        host_url = pecan.request.application_url.rstrip('/')
        if pecan.request.accept is not None and 'yaml' in pecan.request.accept:
            plan_serialized = yamlutils.dump([yaml_content(obj)
                                              for obj in handler.get_all()
                                              if obj and obj.raw_content])
        else:
            plan_serialized = wsme_json.encode_result(
                [plan.Plan.from_db_model(obj, host_url)
                 for obj in handler.get_all()],
                wsme_types.ArrayType(plan.Plan))
        pecan.response.status = 200
        return plan_serialized
