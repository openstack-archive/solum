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

component_policies = [
    policy.DocumentedRuleDefault(
        name='get_components',
        check_str=base.RULE_DEFAULT,
        description='Return all components, based on the query provided.',
        operations=[{'path': '/v1/components',
                     'method': 'GET'}]),
    policy.DocumentedRuleDefault(
        name='show_component',
        check_str=base.RULE_DEFAULT,
        description='Return a component.',
        operations=[{'path': '/v1/components/{component_id}',
                     'method': 'GET'}]),
    policy.DocumentedRuleDefault(
        name='update_component',
        check_str=base.RULE_DEFAULT,
        description='Modify this component.',
        operations=[{'path': '/v1/components/{component_id}',
                     'method': 'PUT'}]),
    policy.DocumentedRuleDefault(
        name='create_component',
        check_str=base.RULE_DEFAULT,
        description='Create a new component.',
        operations=[{'path': '/v1/components',
                     'method': 'POST'}]),
    policy.DocumentedRuleDefault(
        name='delete_component',
        check_str=base.RULE_DEFAULT,
        description='Delete a component.',
        operations=[{'path': '/v1/components/{component_id}',
                     'method': 'DELETE'}])
]


def list_rules():
    return component_policies
