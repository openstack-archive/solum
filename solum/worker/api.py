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

"""API for interfacing with Solum Worker."""

from oslo.config import cfg
from solum.common.rpc import service


STATES = (PENDING, BUILDING, ERROR, COMPLETE) = (
    'PENDING', 'BUILDING', 'ERROR', 'COMPLETE')


class API(service.API):
    def __init__(self, transport=None, context=None):
        cfg.CONF.import_opt('topic', 'solum.worker.config',
                            group='worker')
        super(API, self).__init__(transport, context,
                                  topic=cfg.CONF.worker.topic)

    def build(self, build_id, source_uri, name, base_image_id,
              source_format, image_format, assembly_id=None):
        self._cast('build', build_id=build_id, source_uri=source_uri,
                   name=name, base_image_id=base_image_id,
                   source_format=source_format, image_format=image_format,
                   assembly_id=assembly_id)
