# Copyright 2014 - Rackspace
#
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
import six
import wsme
from wsme import types as wtypes
import wsmeext.pecan as wsme_pecan

from solum.api.controllers.v1.datamodel import language_pack
from solum.api.handlers import language_pack_handler
from solum.common import exception


class LanguagePackController(rest.RestController):
    """Manages operations on a single language pack."""

    def __init__(self, language_pack_id):
        self._id = language_pack_id

    @wsme_pecan.wsexpose(language_pack.LanguagePack, wtypes.text)
    def get(self):
        """Return a language pack."""
        try:
            handler = language_pack_handler.LanguagePackHandler()
            return handler.get(self._id)
        except exception.SolumException as excp:
            pecan.response.translatable_error = excp
            raise wsme.exc.ClientSideError(six.text_type(excp), excp.code)


class LanguagePacksController(rest.RestController):
    """Manages operations on the language packs collection."""

    @pecan.expose()
    def _lookup(self, language_pack_id, *remainder):
        if remainder and not remainder[-1]:
            remainder = remainder[:-1]
        return LanguagePackController(language_pack_id), remainder

    @wsme_pecan.wsexpose([language_pack.LanguagePack])
    def get_all(self):
        """Return all language packs, based on the query provided."""
        try:
            handler = language_pack_handler.LanguagePackHandler()
            return handler.get_all()
        except exception.SolumException as excp:
            pecan.response.translatable_error = excp
            raise wsme.exc.ClientSideError(six.text_type(excp), excp.code)
