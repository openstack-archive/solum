#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from oslo_concurrency import processutils as putils
from oslo_utils import strutils

from solum import privileged


# Entrypoint used for rootwrap.py transition code.  Don't use this for
# other purposes, since it will be removed when we think the
# transition is finished.
def execute(*cmd, **kwargs):
    run_as_root = kwargs.pop('run_as_root', False)
    kwargs.pop('root_helper', None)

    try:
        if run_as_root:
            return execute_root(*cmd, **kwargs)
        else:
            return putils.execute(*cmd, **kwargs)
    except OSError as e:
        sanitized_cmd = strutils.mask_password(' '.join(cmd))
        raise putils.ProcessExecutionError(
            cmd=sanitized_cmd, description=str(e))


@privileged.default.entrypoint
def execute_root(*cmd, **kwargs):
    return putils.execute(*cmd, shell=False, run_as_root=False, **kwargs)
