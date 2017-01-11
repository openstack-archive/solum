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

from solum.api.handlers import plan_handler as solum_plan_handler
from solum import objects


class PlanHandler(solum_plan_handler.PlanHandler):
    def delete(self, id):
        """Override to simply delete the appropriate row in the DB.

        This will raise an exception if any assemblies refer to this plan.
        """
        db_obj = objects.registry.Plan.get_by_uuid(self.context, id)
        self._delete_params(db_obj.id)
        db_obj.destroy(self.context)
