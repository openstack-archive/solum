# Copyright 2014 - Rackspace Hosting
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

import datetime

import solum
from solum.openstack.common import jsonutils as json


class UploaderBase(object):
    context = None
    original_file_path = None
    assembly_id = None
    build_id = None
    stage_name = None
    strategy = None

    def __init__(self, context, original_file_path, assembly_id, build_id,
                 stage_name):
        self.context = context
        self.original_file_path = original_file_path
        self.assembly_id = assembly_id
        self.build_id = build_id
        self.stage_name = stage_name

    def upload(self):
        pass

    def write_userlog_row(self, location, strategy_info=None):
        ulog = solum.objects.registry.Userlog()
        now = datetime.datetime.utcnow()
        ulog.created_at = now
        ulog.updated_at = now
        ulog.assembly_uuid = self.assembly_id
        ulog.location = location
        ulog.strategy = self.strategy
        if strategy_info is None:
            strategy_info = {}
        ulog.strategy_info = json.dumps(strategy_info)
        ulog.create(self.context)
