# Copyright 2014 - Rackspace Hosting.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from solum.api.controllers import common_types


class Execution(common_types.Link):
    @classmethod
    def from_db_model(cls, m, host_url):
        json = {'target_name': m.uuid}
        json['href'] = '%s/v1/%s/%s' % (host_url, m.__resource__, m.uuid)
        return cls(**(json))

    def as_dict(self, db_model):
        return {'uuid': self.target_name}
