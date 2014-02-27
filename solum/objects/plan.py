# Copyright 2014 - Rackspace US, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from solum.common import exception
from solum.objects import base
from solum.openstack.common import log as logging


LOG = logging.getLogger(__name__)


class Plan(base.CrudMixin):
    # Version 1.0: Initial version
    VERSION = '1.0'

    @classmethod
    def _raise_not_found(cls, item_id):
        """Raise a not found exception."""
        raise exception.NotFound(name='application', id=item_id)


class PlanList(list, base.CrudListMixin):
    """List of Plan."""
