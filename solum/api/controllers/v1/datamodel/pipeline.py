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
    and a git trigger. Together they form a working developement "pipeline".
    """

    plan_uri = wtypes.text
    """Link to the plan URI."""

    workbook_name = wtypes.text
    """Name of the workbook in Mistral to use."""

    @classmethod
    def from_db_model(cls, m, host_url):
        obj = super(Pipeline, cls).from_db_model(m, host_url)
        obj.plan_uri = '%s/v1/plans/%s' % (host_url, m.plan_uuid)
        return obj

    @classmethod
    def sample(cls):
        return cls(uri='http://example.com/v2/pipelines/p1',
                   type='pipeline',
                   name='Example-pipeline',
                   description='A pipeline for my app',
                   tags=['small'],
                   project_id='1dae5a09ef2b4d8cbf3594b0eb4f6b94',
                   user_id='55f41cf46df74320b9486a35f5d28a11',
                   plan_uri='http://example.com/v1/plans/x1',
                   workbook_name='build-deploy')
