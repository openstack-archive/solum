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
import re

from oslo_log import log as logging
from oslo_serialization import jsonutils as json

import solum

LOG = logging.getLogger(__name__)


class UploaderBase(object):
    context = None
    original_file_path = None
    resource = None
    stage_id = None
    stage_name = None
    strategy = None

    def __init__(self, context, original_file_path, resource, stage_id,
                 stage_name):
        self.context = context
        self.original_file_path = original_file_path
        self.transformed_path = original_file_path + '.tf'
        self.resource = resource
        self.stage_id = stage_id
        self.stage_name = stage_name

    def upload_log(self):
        pass

    def transform_jsonlog(self):
        with open(self.original_file_path, 'r') as logfile:
            with open(self.transformed_path, 'w') as tflogfile:
                for line in logfile.readlines():
                    try:
                        # Log lines generated from Python logger
                        # has 'level name' followed by ' - '.
                        # Remove this before parsing the log line
                        patrn = ('^ERROR - |^DEBUG - |'
                                 '^WARN - |^CRITICAL - |^INFO - ')
                        reg = re.compile(patrn)
                        m = reg.match(line)
                        if m is not None:
                            line = line.replace(m.group(0), '')
                        json_line = json.loads(line, encoding='utf-8')
                        json_line['user'] = ''
                        if json_line.get('_user') == 'false':
                            # add a suffix to the tag to differentiate user
                            # logs from system logs.
                            json_line['user'] = '.system'
                        flatline = ("%(@timestamp)s "
                                    "solum.%(task)s.%(stage_id)s%(user)s "
                                    "%(message)s\n")
                        tflogfile.write(flatline % json_line)
                    except ValueError:
                        LOG.debug("Could not parse json line: %s", line)

    def write_userlog_row(self, location, strategy_info=None):
        ulog = solum.objects.registry.Userlog()
        now = datetime.datetime.utcnow()
        ulog.created_at = now
        ulog.updated_at = now
        ulog.resource_type = self.resource.type
        ulog.resource_uuid = self.stage_id
        ulog.project_id = self.resource.project_id
        ulog.location = location
        ulog.strategy = self.strategy
        if strategy_info is None:
            strategy_info = {}
        ulog.strategy_info = json.dumps(strategy_info)
        ulog.create(self.context)
