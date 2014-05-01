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

"""Solum Worker shell handler."""

import os
import subprocess

import solum
from solum.conductor import api as conductor_api
from solum.objects import assembly
from solum.objects import image
from solum.openstack.common.gettextutils import _
from solum.openstack.common import log as logging

LOG = logging.getLogger(__name__)

ASSEMBLY_STATES = assembly.States
IMAGE_STATES = image.States


def job_update_notification(ctxt, build_id, status=None, reason=None,
                            created_image_id=None, assembly_id=None):
    """send a status update to the conductor."""
    LOG.debug('build id:%s %s (%s) %s %s' % (build_id, status, reason,
                                             created_image_id, assembly_id),
              context=solum.TLS.trace)
    conductor_api.API(context=ctxt).build_job_update(build_id, status, reason,
                                                     created_image_id,
                                                     assembly_id)


def update_assembly_status(ctxt, assembly_id, status):
    #TODO(datsun180b): use conductor to update assembly status
    assem = solum.objects.registry.Assembly.get_by_id(ctxt,
                                                      assembly_id)
    assem.status = status
    assem.save(ctxt)


class Handler(object):
    def echo(self, ctxt, message):
        LOG.debug(_("%s") % message)

    def build(self, ctxt, build_id, source_uri, name, base_image_id,
              source_format, image_format, assembly_id):

        update_assembly_status(ctxt, assembly_id, ASSEMBLY_STATES.BUILDING)

        solum.TLS.trace.clear()
        solum.TLS.trace.import_context(ctxt)

        proj_dir = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                '..', '..', '..'))
        # map the input formats to script paths.
        # TODO(asalkeld) we need an "auto".
        pathm = {'heroku': 'lp-cedarish',
                 'dib': 'diskimage-builder',
                 'docker': 'docker',
                 'qcow2': 'vm-slug'}
        if base_image_id == 'auto' and image_format == 'qcow2':
            base_image_id = 'cedarish'
        build_app = os.path.join(proj_dir, 'contrib',
                                 pathm.get(source_format, 'lp-cedarish'),
                                 pathm.get(image_format, 'vm-slug'),
                                 'build-app')
        build_cmd = [build_app, source_uri, name, ctxt.tenant, base_image_id]
        solum.TLS.trace.support_info(build_cmd=' '.join(build_cmd),
                                     assembly_id=assembly_id)
        job_update_notification(ctxt, build_id, IMAGE_STATES.BUILDING,
                                reason='Starting the image build',
                                assembly_id=assembly_id)
        try:
            out = subprocess.Popen(build_cmd,
                                   stdout=subprocess.PIPE).communicate()[0]
        except OSError as subex:
            LOG.exception(subex)
            job_update_notification(ctxt, build_id, IMAGE_STATES.ERROR,
                                    reason=subex, assembly_id=assembly_id)
            return
        # we expect one line in the output that looks like:
        # created_image_id=<the glance_id>
        created_image_id = None
        for line in out.split('\n'):
            if 'created_image_id' in line:
                solum.TLS.trace.support_info(build_out_line=line)
                created_image_id = line.split('=')[-1].strip()
        if created_image_id is None:
            job_update_notification(ctxt, build_id, IMAGE_STATES.ERROR,
                                    reason='image not created',
                                    assembly_id=assembly_id)
            return
        job_update_notification(ctxt, build_id, IMAGE_STATES.COMPLETE,
                                reason='built successfully',
                                created_image_id=created_image_id,
                                assembly_id=assembly_id)
