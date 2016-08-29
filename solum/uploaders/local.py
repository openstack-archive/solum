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

from oslo_log import log as logging

import solum.uploaders.common

LOG = logging.getLogger(__name__)


class LocalStorage(solum.uploaders.common.UploaderBase):
    strategy = "local"

    def upload_log(self):
        LOG.debug("Log already stored locally at %s." %
                  self.original_file_path)
        self.write_userlog_row(self.original_file_path)
