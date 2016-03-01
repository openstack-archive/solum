# Copyright 2015 - Rackspace Hosting
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

"""LP handler for building apps running on cedarish build packs"""

from solum.worker.app_handlers import base


class HerokuHandler(base.BaseHandler):

    def __init__(self, context, assembly):
        super(HerokuHandler, self).__init__(context, assembly)

    def unittest_app(self, *args):
        pass

    def build_app(self, *args):
        pass
