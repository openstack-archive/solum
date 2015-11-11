# Copyright 2014 - Rackspace US, Inc.
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

from wsme import types as wtypes

from solum.api.controllers.v1.datamodel import types as api_types


class Pipeline(api_types.Base):
    """Representation of an Pipeline.

    A pipeline is the association between a plan, a mistral workbook
    and a git trigger. Together they form a working development "pipeline".
    """

    plan_uri = wtypes.text
    """Link to the plan URI."""

    workbook_name = wtypes.text
    """Name of the workbook in Mistral to use."""

    trigger_uri = wtypes.text
    """The trigger uri used to trigger the pipeline."""

    last_execution = wtypes.text
    """The UUID of the last run execution."""

    @classmethod
    def from_db_model(cls, m, host_url):
        obj = super(Pipeline, cls).from_db_model(m, host_url)
        le_obj = m.last_execution()
        if le_obj is not None:
            obj.last_execution = le_obj.uuid
        obj.plan_uri = '%s/v1/plans/%s' % (host_url, m.plan_uuid)
        obj.trigger_uri = '%s/v1/triggers/%s' % (host_url, m.trigger_id)
        return obj

    @classmethod
    def sample(cls):
        return cls(uri='http://example.com/v2/pipelines/p1',
                   type='pipeline',
                   name='Example-pipeline',
                   description='A pipeline for my app',
                   trigger_uri='http://example.com/v1/triggers/1abc234',
                   last_execution='78f41cf46df7430b9486a35f5d28a41',
                   tags=['small'],
                   project_id='1dae5a09ef2b4d8cbf3594b0eb4f6b94',
                   user_id='55f41cf46df74320b9486a35f5d28a11',
                   plan_uri='http://example.com/v1/plans/x1',
                   workbook_name='build-deploy')
