# Copyright 2013 - Red Hat, Inc.
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

from solum import objects

from solum.objects import extension as abstract_extension
from solum.objects import operation as abstract_operation
from solum.objects import plan as abstract_plan
from solum.objects import sensor as abstract_sensor
from solum.objects import service as abstract_srvc
from solum.objects.sqlalchemy import extension
from solum.objects.sqlalchemy import operation
from solum.objects.sqlalchemy import plan
from solum.objects.sqlalchemy import sensor
from solum.objects.sqlalchemy import service


def load():
    """Activate the sqlalchemy backend."""
    objects.registry.add(abstract_plan.Plan, plan.Plan)
    objects.registry.add(abstract_plan.PlanList, plan.PlanList)
    objects.registry.add(abstract_srvc.Service, service.Service)
    objects.registry.add(abstract_srvc.ServiceList, service.ServiceList)
    objects.registry.add(abstract_operation.Operation, operation.Operation)
    objects.registry.add(abstract_operation.OperationList,
                         operation.OperationList)
    objects.registry.add(abstract_sensor.Sensor, sensor.Sensor)
    objects.registry.add(abstract_sensor.SensorList, sensor.SensorList)
    objects.registry.add(abstract_extension.Extension, extension.Extension)
    objects.registry.add(abstract_extension.ExtensionList,
                         extension.ExtensionList)
