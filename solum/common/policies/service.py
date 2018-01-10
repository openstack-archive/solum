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

service_policies = [
    policy.DocumentedRuleDefault(
        name='get_services',
        check_str=base.RULE_DEFAULT,
        description='Return all services, based on the query provided.',
        operations=[{'path': '/v1/services',
                     'method': 'GET'}]),
    policy.DocumentedRuleDefault(
        name='show_service',
        check_str=base.RULE_DEFAULT,
        description='Return a service.',
        operations=[{'path': '/v1/services/{service_id}',
                     'method': 'GET'}]),
    policy.DocumentedRuleDefault(
        name='update_service',
        check_str=base.RULE_DEFAULT,
        description='Modify this service.',
        operations=[{'path': '/v1/services/{service_id}',
                     'method': 'PUT'}]),
    policy.DocumentedRuleDefault(
        name='create_service',
        check_str=base.RULE_DEFAULT,
        description='Create a new service.',
        operations=[{'path': '/v1/services',
                     'method': 'POST'}]),
    policy.DocumentedRuleDefault(
        name='delete_service',
        check_str=base.RULE_DEFAULT,
        description='Delete a service.',
        operations=[{'path': '/v1/services/{service_id}',
                     'method': 'DELETE'}])
]


def list_rules():
    return service_policies
