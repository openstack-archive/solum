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

languagepack_policies = [
    policy.DocumentedRuleDefault(
        name='get_languagepacks',
        check_str=base.RULE_DEFAULT,
        description='Return all languagepacks, based on the query provided.',
        operations=[{'path': '/v1/language_packs',
                     'method': 'GET'}]),
    policy.DocumentedRuleDefault(
        name='show_languagepack',
        check_str=base.RULE_DEFAULT,
        description='Return a languagepack.',
        operations=[{'path': '/v1/language_packs/{lp_id}',
                     'method': 'GET'}]),
    policy.DocumentedRuleDefault(
        name='create_languagepack',
        check_str=base.RULE_DEFAULT,
        description='Create a new languagepack.',
        operations=[{'path': '/v1/language_packs',
                     'method': 'POST'}]),
    policy.DocumentedRuleDefault(
        name='delete_languagepack',
        check_str=base.RULE_DEFAULT,
        description='Delete a languagepack.',
        operations=[{'path': '/v1/language_packs/{lp_id}',
                     'method': 'DELETE'}])
]


def list_rules():
    return languagepack_policies
