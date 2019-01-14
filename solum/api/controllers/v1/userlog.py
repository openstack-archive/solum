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

import pecan
from pecan import rest
import wsmeext.pecan as wsme_pecan

from solum.api.controllers.v1.datamodel import userlog
from solum.api.handlers import userlog_handler
from solum.common import exception


class UserlogsController(rest.RestController):
    """Manages operations on the Userlogs collection."""

    def __init__(self, resource_id):
        super(UserlogsController, self).__init__()
        self._resource_id = resource_id

    @exception.wrap_wsme_pecan_controller_exception
    @wsme_pecan.wsexpose([userlog.Userlog])
    def get_all(self):
        """Return all Userlogs, based on the query provided."""
        handler = userlog_handler.UserlogHandler(
            pecan.request.security_context)
        ulogs = handler.get_all_by_id(self._resource_id)
        host_url = pecan.request.application_url.rstrip('/')
        return [userlog.Userlog.from_db_model(ulog, host_url)
                for ulog in ulogs]
