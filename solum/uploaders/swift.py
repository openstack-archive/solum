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

from oslo.config import cfg

from solum.common import clients
from solum.openstack.common import log as logging
import solum.uploaders.common

from swiftclient import exceptions as swiftexceptions

LOG = logging.getLogger(__name__)

cfg.CONF.import_opt('log_upload_swift_container', 'solum.worker.config',
                    group='worker')


class SwiftUpload(solum.uploaders.common.UploaderBase):
    strategy = "swift"

    def upload(self):
        container = cfg.CONF.worker.log_upload_swift_container
        filename = "%s/%s-%s.log" % (self.assembly_id, self.build_id,
                                     self.stage_name)
        with open(self.original_file_path, 'r') as logfile:
            try:
                LOG.debug("Uploading log to Swift. %s, %s" %
                          (container, filename))
                swift = clients.OpenStackClients(self.context).swift()
                swift.put_container(container)
                swift.put_object(container, filename, logfile)
            except swiftexceptions.ClientException:
                LOG.exception("Failed to upload logfile to Swift.")
            LOG.debug("Logfile uploaded to Swift.")

        swift_info = {
            'container': container,
        }

        self.write_userlog_row(self.original_file_path, swift_info)
