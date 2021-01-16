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

from oslo_config import cfg

from solum.common.rpc import service


class API(service.API):
    def __init__(self, context=None):
        cfg.CONF.import_opt('topic', 'solum.conductor.config',
                            group='conductor')
        super(API, self).__init__(context,
                                  topic=cfg.CONF.conductor.topic)

    def build_job_update(self, build_id, status, description, created_image_id,
                         docker_image_name, assembly_id):
        self._cast('build_job_update', build_id=build_id, status=status,
                   description=description, created_image_id=created_image_id,
                   docker_image_name=docker_image_name,
                   assembly_id=assembly_id)

    def update_assembly(self, assembly_id, data):
        self._cast('update_assembly', assembly_id=assembly_id, data=data)

    def update_image(self, image_id, status, external_ref=None,
                     docker_image_name=None):
        self._cast('update_image', image_id=image_id, status=status,
                   external_ref=external_ref,
                   docker_image_name=docker_image_name)
