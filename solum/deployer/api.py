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

"""API for interfacing with Solum Deployer."""

from oslo_config import cfg

from solum.common.rpc import service


class API(service.API):
    def __init__(self, context=None):
        cfg.CONF.import_opt('topic', 'solum.deployer.config',
                            group='deployer')
        super(API, self).__init__(context,
                                  topic=cfg.CONF.deployer.topic)

    def deploy(self, assembly_id, image_loc, image_name, ports):
        self._cast('deploy', assembly_id=assembly_id, image_loc=image_loc,
                   image_name=image_name, ports=ports)

    def scale(self, assembly_id):
        self._cast('scale', assembly_id=assembly_id)

    def destroy_assembly(self, assem_id):
        self._cast('destroy_assembly', assem_id=assem_id)

    def destroy_app(self, app_id):
        self._cast('destroy_app', app_id=app_id)
