# Copyright 2014 - Rackspace Hosting
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

import json
import os

from swiftclient import exceptions as swiftexp

from solum.api.handlers import handler
from solum.common import exception as exc
from solum.common import solum_swiftclient
from solum import objects


class UserlogHandler(handler.Handler):

    def get_all(self):
        """Return all userlogs, based on the query provided."""
        return objects.registry.UserlogList.get_all(self.context)

    def get_all_by_id(self, resource_uuid):
        return objects.registry.UserlogList.get_all_by_id(
            self.context, resource_uuid=resource_uuid)

    def delete(self, resource_uuid):
        """Delete existing logs."""
        ulogs = objects.registry.UserlogList.get_all_by_id(
            self.context, resource_uuid=resource_uuid)

        # Delete log files
        swift = solum_swiftclient.SwiftClient(self.context)
        for ulog in ulogs:
            location = ulog.location
            strategy = ulog.strategy
            strategy_info = json.loads(ulog.strategy_info)
            if strategy == 'swift':
                # Delete logs from swift
                try:
                    swift.delete_object(strategy_info['container'],
                                        location)
                except swiftexp.ClientException:
                    raise exc.AuthorizationFailure(
                        client='swift',
                        message="Unable to delete logs from swift.")
            elif strategy == 'local':
                # Delete logs from local filesystem
                # This setting is exclusively used for single node deployments.
                try:
                    os.remove(location)
                except OSError:
                    pass

            # Delete the log reference from db.
            ulog.destroy(self.context)

        return
