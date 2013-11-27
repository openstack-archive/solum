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

import pecan
from pecan import rest
import wsme
from wsme import types as wtypes
import wsmeext.pecan as wsme_pecan

from solum.api.controllers import common_types


class Extension(wtypes.Base):
    """The Extension resource represents changes that the Provider has added
    onto a Platform in addition to the ones supplied by Solum by default.
    This may include additional protocol semantics, resource types,
    application lifecycle states, resource attributes, etc. Anything may be
    added, as long as it does not contradict the base functionality offered
    by Solum.
    """

    uri = common_types.Uri
    "Uri to the extension"

    name = wtypes.text
    "Name of the extension"

    type = wtypes.text
    "Extension type"

    description = wtypes.text
    "Description of the extension"

    version = wtypes.text
    "Version of the extension"

    documentation = common_types.Uri
    "Documentation uri to the extension"

    @classmethod
    def sample(cls):
        return cls(uri='http://example.com/v1/extensions/mysql',
                   name='mysql',
                   type='extension',
                   description='A mysql extension',
                   version='2.13',
                   documentation='http://example.com/docs/ext/mysql')


class ExtensionController(rest.RestController):
    """Manages operations on a single extension."""

    def __init__(self, extension_id):
        pecan.request.context['extension_id'] = extension_id
        self._id = extension_id

    @wsme_pecan.wsexpose(Extension, wtypes.text)
    def get(self):
        """Return this extension."""
        error = _("Not implemented")
        pecan.response.translatable_error = error
        raise wsme.exc.ClientSideError(unicode(error))


class Extensions(wtypes.Base):
    """A collection of extensions returned on listing.
    """

    uri = common_types.Uri
    "Uri to the Extensions"

    name = wtypes.text
    "Name of the extension"

    type = wtypes.text
    "Extension type"

    description = wtypes.text
    "Description of the extension"

    extension_links = [common_types.Link]
    "List of links to the available extensions"

    @classmethod
    def sample(cls):
        return cls(uri='http://example.com/v1/extensions',
                   extension_links=[common_types.Link(
                       href='http://example.com:9777/v1/extensions/y4',
                       target_name='y4')])


class ExtensionsController(rest.RestController):
    """Manages operations on the extensions collection."""

    @pecan.expose()
    def _lookup(self, extension_id, *remainder):
        if remainder and not remainder[-1]:
            remainder = remainder[:-1]
        return ExtensionController(extension_id), remainder

    @wsme_pecan.wsexpose(Extensions)
    def get_all(self):
        """Return all extensions, based on the query provided."""
        host_url = '/'.join([pecan.request.host_url, 'v1', 'extensions'])
        return Extensions(uri=host_url,
                          type='extensions',
                          description='Collection of extensions',
                          extension_links=[])
