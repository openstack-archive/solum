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

import sys

from oslo_config import cfg
from oslo_db.sqlalchemy import session


_FACADE = None


def get_facade():
    global _FACADE

    if not _FACADE:
        _FACADE = session.EngineFacade.from_config(cfg.CONF)
    return _FACADE


def get_engine():
    return get_facade().get_engine()


def get_session():
    return get_facade().get_session()


def get_backend():
    """The backend is this module itself."""
    return sys.modules[__name__]


def cleanup():
    global _FACADE

    if _FACADE:
        _FACADE.get_engine().dispose()
        _FACADE = None


def load():
    """Activate the sqlalchemy backend."""
    from solum import objects
    from solum.objects import app as abstract_app
    from solum.objects import assembly as abstract_assembly
    from solum.objects import component as abstract_component
    from solum.objects import execution as abstract_execution
    from solum.objects import extension as abstract_extension
    from solum.objects import image as abstract_image
    from solum.objects import infrastructure_stack as abstract_infra_stack
    from solum.objects import operation as abstract_operation
    from solum.objects import parameter as abstract_parameter
    from solum.objects import pipeline as abstract_pipeline
    from solum.objects import plan as abstract_plan
    from solum.objects import sensor as abstract_sensor
    from solum.objects import service as abstract_srvc
    from solum.objects.sqlalchemy import app
    from solum.objects.sqlalchemy import assembly
    from solum.objects.sqlalchemy import component
    from solum.objects.sqlalchemy import execution
    from solum.objects.sqlalchemy import extension
    from solum.objects.sqlalchemy import image
    from solum.objects.sqlalchemy import infrastructure_stack
    from solum.objects.sqlalchemy import operation
    from solum.objects.sqlalchemy import parameter
    from solum.objects.sqlalchemy import pipeline
    from solum.objects.sqlalchemy import plan
    from solum.objects.sqlalchemy import sensor
    from solum.objects.sqlalchemy import service
    from solum.objects.sqlalchemy import userlog
    from solum.objects.sqlalchemy import workflow
    from solum.objects import userlog as abstract_userlog
    from solum.objects import workflow as abstract_workflow

    objects.registry.add(abstract_app.App, app.App)
    objects.registry.add(abstract_app.AppList, app.AppList)
    objects.registry.add(abstract_assembly.Assembly, assembly.Assembly)
    objects.registry.add(abstract_assembly.AssemblyList, assembly.AssemblyList)
    objects.registry.add(abstract_infra_stack.InfrastructureStack,
                         infrastructure_stack.InfrastructureStack)
    objects.registry.add(abstract_infra_stack.InfrastructureStackList,
                         infrastructure_stack.InfrastructureStackList)
    objects.registry.add(abstract_component.Component, component.Component)
    objects.registry.add(abstract_component.ComponentList,
                         component.ComponentList)
    objects.registry.add(abstract_plan.Plan, plan.Plan)
    objects.registry.add(abstract_plan.PlanList, plan.PlanList)
    objects.registry.add(abstract_pipeline.Pipeline, pipeline.Pipeline)
    objects.registry.add(abstract_pipeline.PipelineList, pipeline.PipelineList)
    objects.registry.add(abstract_execution.Execution, execution.Execution)
    objects.registry.add(abstract_execution.ExecutionList,
                         execution.ExecutionList)
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
    objects.registry.add(abstract_image.Image, image.Image)
    objects.registry.add(abstract_image.ImageList, image.ImageList)
    objects.registry.add(abstract_userlog.Userlog, userlog.Userlog)
    objects.registry.add(abstract_userlog.UserlogList, userlog.UserlogList)
    objects.registry.add(abstract_parameter.Parameter, parameter.Parameter)
    objects.registry.add(abstract_parameter.ParameterList,
                         parameter.ParameterList)
    objects.registry.add(abstract_workflow.Workflow, workflow.Workflow)
    objects.registry.add(abstract_workflow.WorkflowList, workflow.WorkflowList)
