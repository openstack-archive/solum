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

"""Solum Worker shell handler, with build dummied out."""

from solum.objects import assembly
from solum.openstack.common import log as logging
from solum.worker.handlers import shell as shell_handler

LOG = logging.getLogger(__name__)

ASSEMBLY_STATES = assembly.States

job_update_notification = shell_handler.job_update_notification
update_assembly_status = shell_handler.update_assembly_status


class Handler(shell_handler.Handler):
    def build(self, ctxt, build_id, git_info, name, base_image_id,
              source_format, image_format, assembly_id,
              test_cmd, source_creds_ref=None):

        # TODO(datsun180b): This is only temporary, until Mistral becomes our
        # workflow engine.
        ret_code = 0
        status_url = git_info.get('status_url')
        status_token = git_info.get('status_token')

        self._send_status(ret_code, status_url, status_token, pending=True)
        ret_code = self._run_unittest(ctxt, assembly_id, git_info, test_cmd,
                                      source_creds_ref)
        self._send_status(ret_code, status_url, status_token)

        # Deployer is normally in charge of declaring an assembly READY.
        if ret_code == 0:
            update_assembly_status(ctxt, assembly_id, ASSEMBLY_STATES.READY)
