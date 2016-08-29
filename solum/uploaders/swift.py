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

from oslo_config import cfg
from oslo_log import log as logging

from solum.common import exception as exc
from solum.common import solum_swiftclient as swiftclient
import solum.uploaders.common

from swiftclient import exceptions as swiftexp

LOG = logging.getLogger(__name__)

cfg.CONF.import_opt('log_upload_swift_container', 'solum.worker.config',
                    group='worker')


class SwiftUpload(solum.uploaders.common.UploaderBase):
    strategy = "swift"

    def _upload(self, container, filename, filepath):
        swift = swiftclient.SwiftClient(self.context)
        swift.upload(filepath, container, filename)

    def upload_log(self):
        container = cfg.CONF.worker.log_upload_swift_container
        filename = "%s-%s/%s-%s.log" % (self.resource.name, self.stage_id,
                                        self.stage_name, self.stage_id)

        self.transform_jsonlog()
        try:
            LOG.debug("Uploading log to Swift. %s, %s" %
                      (container, filename))
            self._upload(container, filename, self.transformed_path)
        except exc.InvalidObjectSizeError:
            LOG.exception("Unable to upload logfile: %s to swift. "
                          "Invalid size." % self.transformed_path)
            return
        except swiftexp.ClientException:
            LOG.exception("Failed to upload logfile: %s to Swift." %
                          self.transformed_path)
            return
        LOG.debug("Logfile uploaded to Swift.")

        swift_info = {
            'container': container,
        }

        self.write_userlog_row(filename, swift_info)
