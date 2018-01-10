# Copyright 2017 AT&T Corporation.
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

import itertools

from solum.common.policies import assembly
from solum.common.policies import base
from solum.common.policies import component
from solum.common.policies import extension
from solum.common.policies import languagepack
from solum.common.policies import operation
from solum.common.policies import pipeline
from solum.common.policies import plan
from solum.common.policies import sensor
from solum.common.policies import service
from solum.common.policies import trigger


def list_rules():
    return itertools.chain(
        assembly.list_rules(),
        base.list_rules(),
        component.list_rules(),
        extension.list_rules(),
        languagepack.list_rules(),
        operation.list_rules(),
        pipeline.list_rules(),
        plan.list_rules(),
        sensor.list_rules(),
        service.list_rules(),
        trigger.list_rules(),
    )
