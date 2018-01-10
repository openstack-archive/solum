# Copyright 2018 ZTE Corporation.
# All Rights Reserved.
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

from oslo_policy import policy

from solum.common.policies import base

pipeline_policies = [
    policy.DocumentedRuleDefault(
        name='get_pipelines',
        check_str=base.RULE_DEFAULT,
        description='Return all pipelines, based on the query provided.',
        operations=[{'path': '/v1/pipelines',
                     'method': 'GET'}]),
    policy.DocumentedRuleDefault(
        name='show_pipeline',
        check_str=base.RULE_DEFAULT,
        description='Return a pipeline.',
        operations=[{'path': '/v1/pipelines/{pipeline_id}',
                     'method': 'GET'}]),
    policy.DocumentedRuleDefault(
        name='update_pipeline',
        check_str=base.RULE_DEFAULT,
        description='Modify this pipeline.',
        operations=[{'path': '/v1/pipelines/{pipeline_id}',
                     'method': 'PUT'}]),
    policy.DocumentedRuleDefault(
        name='get_pipeline_executions',
        check_str=base.RULE_DEFAULT,
        description='Return all executions, based on the pipeline_id.',
        operations=[{'path': '/v1/pipelines/{pipeline_id}/executions',
                     'method': 'GET'}]),
    policy.DocumentedRuleDefault(
        name='create_pipeline',
        check_str=base.RULE_DEFAULT,
        description='Create a new pipeline.',
        operations=[{'path': '/v1/pipelines',
                     'method': 'POST'}]),
    policy.DocumentedRuleDefault(
        name='delete_pipeline',
        check_str=base.RULE_DEFAULT,
        description='Delete a pipeline.',
        operations=[{'path': '/v1/pipelines/{pipeline_id}',
                     'method': 'DELETE'}])
]


def list_rules():
    return pipeline_policies
