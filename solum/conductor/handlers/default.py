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

"""Solum Conductor default handler."""

from oslo_log import log as logging
from sqlalchemy import exc as sqla_exc

from solum import objects
from solum.objects import assembly

LOG = logging.getLogger(__name__)

ASSEMBLY_STATES = assembly.States


class Handler(object):
    def __init__(self):
        super(Handler, self).__init__()
        objects.load()

    def echo(self, ctxt, message):
        LOG.debug("%s" % message)

    def build_job_update(self, ctxt, build_id, status, description,
                         created_image_id, docker_image_name, assembly_id):
        to_update = {'status': status,
                     'external_ref': created_image_id,
                     'docker_image_name': docker_image_name,
                     'description': str(description)}
        try:
            objects.registry.Image.update_and_save(ctxt, build_id, to_update)
        except sqla_exc.SQLAlchemyError as ex:
            LOG.error("Failed to update image, ID: %s" % build_id)
            LOG.exception(ex)

        # create the component if needed.
        if assembly_id is None:
            return
        try:
            assem = objects.registry.Assembly.get_by_id(ctxt,
                                                        assembly_id)
            if assem.status == ASSEMBLY_STATES.DELETING:
                return
            if not any([comp for comp in assem.components
                        if 'Image_Build' in comp.description]):
                comp_name = "Heat_Stack_for_%s" % assem.name
                stack_id = None
                if assem.heat_stack_component is not None:
                    stack_id = assem.heat_stack_component.heat_stack_id
                objects.registry.Component.assign_and_create(ctxt, assem,
                                                             comp_name,
                                                             'Image_Build',
                                                             'Image Build job',
                                                             created_image_id,
                                                             stack_id)
                # update reference to image in assembly
                assem_update = {'image_id': build_id}
                objects.registry.Assembly.update_and_save(ctxt,
                                                          assembly_id,
                                                          assem_update)
        except sqla_exc.IntegrityError:
            LOG.error("IntegrityError in creating Image_Build component,"
                      " assembly %s may be deleted" % assembly_id)

    def update_assembly(self, ctxt, assembly_id, data):
        try:
            objects.registry.Assembly.update_and_save(ctxt, assembly_id, data)
        except sqla_exc.SQLAlchemyError as ex:
            LOG.error("Failed to update assembly status, ID: %s" % assembly_id)
            LOG.exception(ex)

    def update_image(self, ctxt, image_id, status, external_ref=None,
                     docker_image_name=None):
        to_update = {'status': status}
        if external_ref:
            to_update['external_ref'] = external_ref
        if docker_image_name:
            to_update['docker_image_name'] = docker_image_name
        try:
            objects.registry.Image.update_and_save(ctxt, image_id, to_update)
        except sqla_exc.SQLAlchemyError as ex:
            LOG.error("Failed to update image, ID: %s" % image_id)
            LOG.exception(ex)
