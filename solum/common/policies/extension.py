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

extension_policies = [
    policy.DocumentedRuleDefault(
        name='get_extensions',
        check_str=base.RULE_DEFAULT,
        description='Return all extensions, based on the query provided.',
        operations=[{'path': '/v1/extensions',
                     'method': 'GET'}]),
    policy.DocumentedRuleDefault(
        name='show_extension',
        check_str=base.RULE_DEFAULT,
        description='Return a extension.',
        operations=[{'path': '/v1/extensions/{extension_id}',
                     'method': 'GET'}]),
    policy.DocumentedRuleDefault(
        name='update_extension',
        check_str=base.RULE_DEFAULT,
        description='Modify this extension.',
        operations=[{'path': '/v1/extensions/{extension_id}',
                     'method': 'PUT'}]),
    policy.DocumentedRuleDefault(
        name='create_extension',
        check_str=base.RULE_DEFAULT,
        description='Create a new extension.',
        operations=[{'path': '/v1/extensions',
                     'method': 'POST'}]),
    policy.DocumentedRuleDefault(
        name='delete_extension',
        check_str=base.RULE_DEFAULT,
        description='Delete a extension.',
        operations=[{'path': '/v1/extensions/{extension_id}',
                     'method': 'DELETE'}])
]


def list_rules():
    return extension_policies
