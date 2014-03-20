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

"""API for interfacing with Solum Conductor."""

from oslo.config import cfg
from solum.common.rpc import service


class API(service.API):
    def __init__(self, transport=None, context=None):
        cfg.CONF.import_opt('topic', 'solum.conductor.config',
                            group='conductor')
        super(API, self).__init__(transport, context,
                                  topic=cfg.CONF.conductor.topic)

    def build_job_update(self, id, status, reason, created_image_id,
                         assembly_id):
        self._cast('build_job_update', id=id, status=status, reason=reason,
                   created_image_id=created_image_id, assembly_id=assembly_id)
