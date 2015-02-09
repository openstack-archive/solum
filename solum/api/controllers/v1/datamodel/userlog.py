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

from wsme import types as wtypes


class Userlog(wtypes.Base):

    resource_uuid = wtypes.text
    resource_type = wtypes.text
    created_at = wtypes.text
    location = wtypes.text
    strategy = wtypes.text
    strategy_info = wtypes.text

    def __init__(self, **kwargs):
        super(Userlog, self).__init__(**kwargs)

    @classmethod
    def from_db_model(cls, m, host_url):
        return cls(
            resource_uuid=m.resource_uuid,
            resource_type=m.resource_type,
            created_at=str(m.created_at),
            location=m.location,
            strategy=m.strategy,
            strategy_info=m.strategy_info,
            )
