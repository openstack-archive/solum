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

"""Solum Worker handler."""

from oslo_log import log as logging

from solum.common import exception
from solum.conductor import api as conductor_api
from solum.deployer import api as deployer_api
from solum import objects
from solum.objects import assembly
from solum.objects import image
from solum.worker.app_handlers import default as docker_handler


LOG = logging.getLogger(__name__)

ASSEMBLY_STATES = assembly.States
IMAGE_STATES = image.States


def job_update_notification(ctxt, build_id, status=None, description=None,
                            created_image_id=None, docker_image_name=None,
                            assembly_id=None):
    """send a status update to the conductor."""
    conductor_api.API(context=ctxt).build_job_update(build_id, status,
                                                     description,
                                                     created_image_id,
                                                     docker_image_name,
                                                     assembly_id)


def update_assembly_status(ctxt, assembly_id, status):
    if assembly_id is None:
        return
    data = {'status': status}
    conductor_api.API(context=ctxt).update_assembly(assembly_id, data)


def update_lp_status(ctxt, image_id, status, external_ref=None,
                     docker_image_name=None):
    if image_id is None:
        return
    LOG.debug('Updating languagepack %s status to %s and external_ref to %s'
              % (image_id, status, external_ref))
    conductor_api.API(context=ctxt).update_image(image_id, status,
                                                 external_ref,
                                                 docker_image_name)


def validate_lp(ctxt, lp_id, assembly_id):
    try:
        image = objects.registry.Image.get_lp_by_name_or_uuid(
            ctxt, lp_id, include_operators_lp=True)
    except exception.ObjectNotFound:
        LOG.error('LP not found with id %s, assembly id: %s' %
                  (lp_id, assembly_id))
        return

    if (not image or not image.project_id or not image.status or
        not image.external_ref or not image.docker_image_name or
            image.status.lower() != 'ready'):
        LOG.warning("Error building due to language pack %s not ready."
                    " assembly ID: %s" % (lp_id, assembly_id))
        return

    return image


class Handler(object):
    def echo(self, ctxt, message):
        LOG.debug("%s" % message)

    def launch_workflow(self, ctxt, build_id, git_info, ports, name,
                        base_image_id, source_format, image_format,
                        assembly_id, workflow, test_cmd, run_cmd):
        try:
            assem = objects.registry.Assembly.get_by_id(ctxt, assembly_id)
        except exception.ObjectNotFound:
            return

        enable_unittest = enable_build = enable_deploy = False
        for step in workflow:
            if step == 'unittest':
                enable_unittest = True
            elif step == 'build':
                enable_build = True
            elif step == 'deploy':
                enable_deploy = True

        du_image_loc = None
        du_image_name = None
        with docker_handler.DockerHandler(ctxt, assem, 'custom',
                                          'swift') as lp_handler:
            if enable_unittest:
                if self._do_unittest(ctxt, lp_handler, build_id, git_info,
                                     name, base_image_id, source_format,
                                     image_format, assembly_id, test_cmd) != 0:
                    return
            if enable_build:
                du_image_loc, du_image_name = self._do_build(
                    ctxt, lp_handler, build_id, git_info, name, base_image_id,
                    source_format, image_format, assembly_id, run_cmd)

        if enable_deploy and du_image_loc and du_image_name:
            self._do_deploy(ctxt, assembly_id, ports, du_image_loc,
                            du_image_name)

    def build(self, ctxt, build_id, git_info, name, base_image_id,
              source_format, image_format, assembly_id, run_cmd):
        try:
            assem = objects.registry.Assembly.get_by_id(ctxt, assembly_id)
        except exception.ObjectNotFound:
            return

        with docker_handler.DockerHandler(ctxt, assem, 'custom',
                                          'swift') as lp_handler:
            self._do_build(ctxt, lp_handler, build_id, git_info, name,
                           base_image_id, source_format, image_format,
                           assembly_id, run_cmd)

    def unittest(self, ctxt, build_id, git_info, name, base_image_id,
                 source_format, image_format, assembly_id, test_cmd):
        try:
            assem = objects.registry.Assembly.get_by_id(ctxt, assembly_id)
        except exception.ObjectNotFound:
            return

        with docker_handler.DockerHandler(ctxt, assem, 'custom',
                                          'swift') as lp_handler:
            self._do_unittest(ctxt, lp_handler, build_id, git_info, name,
                              base_image_id, source_format, image_format,
                              assembly_id, test_cmd)

    def _do_deploy(self, ctxt, assembly_id, ports, du_image_loc,
                   du_image_name):
        deployer_api.API(context=ctxt).deploy(assembly_id=assembly_id,
                                              image_loc=du_image_loc,
                                              image_name=du_image_name,
                                              ports=ports)

    def _do_build(self, ctxt, lp_handler, build_id, git_info, name,
                  base_image_id, source_format, image_format, assembly_id,
                  run_cmd):
        lp = validate_lp(ctxt, base_image_id, assembly_id)
        if not lp:
            update_assembly_status(ctxt, assembly_id, ASSEMBLY_STATES.ERROR)
            job_update_notification(ctxt, build_id, IMAGE_STATES.ERROR,
                                    description='language pack not ready',
                                    assembly_id=assembly_id)
            return

        # Check if the assembly is deleted or being deleted
        try:
            assem = objects.registry.Assembly.get_by_id(ctxt, assembly_id)
            if assem.status == ASSEMBLY_STATES.DELETING:
                LOG.debug('Assembly %s is being deleted..skipping next stages'
                          % assembly_id)
                return
        except exception.ObjectNotFound:
            LOG.debug('Assembly %s was deleted, skipping building.' %
                      assembly_id)
            return

        update_assembly_status(ctxt, assembly_id, ASSEMBLY_STATES.BUILDING)
        image_info = lp_handler.build_app(name, git_info, lp.external_ref,
                                          lp.docker_image_name, run_cmd)
        if not image_info:
            job_update_notification(ctxt, build_id, IMAGE_STATES.ERROR,
                                    description='image not created',
                                    assembly_id=assembly_id)
            update_assembly_status(ctxt, assembly_id, ASSEMBLY_STATES.ERROR)
            return
        else:
            job_update_notification(ctxt, build_id, IMAGE_STATES.READY,
                                    description='built successfully',
                                    created_image_id=image_info[0],
                                    docker_image_name=image_info[1],
                                    assembly_id=assembly_id)
            update_assembly_status(ctxt, assembly_id, ASSEMBLY_STATES.BUILT)
            return (image_info[0], image_info[1])

    def _do_unittest(self, ctxt, lp_handler, build_id, git_info, name,
                     base_image_id, source_format, image_format, assembly_id,
                     test_cmd):
        if test_cmd is None:
            LOG.debug("Unit test command is None; skipping unittests.")
            return 0

        lp = validate_lp(ctxt, base_image_id, assembly_id)
        if not lp:
            update_assembly_status(ctxt, assembly_id, ASSEMBLY_STATES.ERROR)
            return -1

        # Check if the assembly is deleted or being deleted
        try:
            assem = objects.registry.Assembly.get_by_id(ctxt, assembly_id)
            if assem.status == ASSEMBLY_STATES.DELETING:
                LOG.debug('Assembly %s is being deleted..skipping next stages'
                          % assembly_id)
                return -1
        except exception.ObjectNotFound:
            LOG.debug('Assembly %s was deleted, skipping unittesting.' %
                      assembly_id)
            return -1

        update_assembly_status(ctxt, assembly_id, ASSEMBLY_STATES.UNIT_TESTING)
        result = lp_handler.unittest_app(git_info, lp.external_ref,
                                         lp.docker_image_name, test_cmd)
        if result == 0:
            status = ASSEMBLY_STATES.UNIT_TESTING_PASSED
        elif result > 0:
            status = ASSEMBLY_STATES.UNIT_TESTING_FAILED
        else:
            status = ASSEMBLY_STATES.ERROR

        update_assembly_status(ctxt, assembly_id, status)
        return result

    def build_lp(self, ctxt, image_id, git_info, name, source_format,
                 image_format, artifact_type):
        try:
            lp = objects.registry.Image.get_by_id(ctxt, image_id)
        except exception.ObjectNotFound:
            LOG.error('Image object not found with id %s' % image_id)
            return

        update_lp_status(ctxt, image_id, IMAGE_STATES.BUILDING)
        lp.type = 'languagepack'

        image_info = None
        with docker_handler.DockerHandler(ctxt, lp, 'custom', 'swift') as lph:
            image_info = lph.build_lp(name, git_info)
        if image_info:
            status = IMAGE_STATES.READY
            update_lp_status(ctxt, image_id, status, image_info[0],
                             image_info[1])
        else:
            status = IMAGE_STATES.ERROR
            update_lp_status(ctxt, image_id, status)
