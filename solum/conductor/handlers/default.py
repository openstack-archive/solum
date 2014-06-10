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

from solum import objects
from solum.objects import image
from solum.openstack.common import log as logging

LOG = logging.getLogger(__name__)

IMAGE_STATES = image.States


class Handler(object):
    def __init__(self):
        super(Handler, self).__init__()
        objects.load()

    def echo(self, ctxt, message):
        LOG.debug("%s" % message)

    def build_job_update(self, ctxt, build_id, state, description,
                         created_image_id, assembly_id):
        image = objects.registry.Image.get_by_id(ctxt, build_id)
        image.state = state
        image.description = description
        image.created_image_id = created_image_id
        image.save(ctxt)

        # create the component if needed.
        if assembly_id is not None:
            assem = objects.registry.Assembly.get_by_id(ctxt,
                                                        assembly_id)
            if not any([comp for comp in assem.components
                        if 'Image Build' in comp.description]):
                objects.registry.Component.assign_and_create(ctxt, assem,
                                                             'Image Build',
                                                             'Image Build job',
                                                             created_image_id)
