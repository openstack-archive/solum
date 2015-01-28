# Copyright 2014 - Rackspace
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

from solum.objects import base


class Assembly(base.CrudMixin):
    # Version 1.0: Initial version
    VERSION = '1.0'


class AssemblyList(list, base.CrudListMixin):
    """List of Assemblies."""


class States(object):
    QUEUED = 'QUEUED'
    UNIT_TESTING = 'UNIT_TESTING'
    UNIT_TESTING_FAILED = 'UNIT_TESTING_FAILED'
    BUILDING = 'BUILDING'
    DEPLOYING = 'DEPLOYING'
    ERROR = 'ERROR'
    READY = 'READY'
    DELETING = 'DELETING'
    ERROR_STACK_DELETE_FAILED = 'ERROR_STACK_DELETE_FAILED'
    ERROR_STACK_CREATE_FAILED = 'ERROR_STACK_CREATE_FAILED'
    ERROR_DU_CREATION = 'ERROR_DU_CREATION'
    WAITING_FOR_DOCKER_DU = 'WAITING_FOR_DOCKER_DU'
