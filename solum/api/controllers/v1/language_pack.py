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
import wsmeext.pecan as wsme_pecan

from solum.api.controllers.v1.datamodel import language_pack as lp
from solum.api.handlers import language_pack_handler as lp_handler
from solum.common import exception
from solum import objects


class LanguagePackController(rest.RestController):
    """Manages operations on a single language_pack."""

    def __init__(self, language_pack_id):
        super(LanguagePackController, self).__init__()
        self._id = language_pack_id

    @exception.wrap_controller_exception
    @wsme_pecan.wsexpose(lp.LanguagePack)
    def get(self):
        """Return a language_pack."""
        handler = lp_handler.LanguagePackHandler(
            pecan.request.security_context)
        return lp.LanguagePack.from_image(
            handler.get(self._id), pecan.request.host_url)

    @exception.wrap_controller_exception
    @wsme_pecan.wsexpose(lp.LanguagePack, body=lp.LanguagePack)
    def put(self, data):
        """Modify this language_pack."""
        handler = lp_handler.LanguagePackHandler(
            pecan.request.security_context)
        res = handler.update(self._id,
                             data.as_dict(objects.registry.LanguagePack))
        return lp.LanguagePack.from_db_model(res, pecan.request.host_url)

    @exception.wrap_controller_exception
    @wsme_pecan.wsexpose(status_code=204)
    def delete(self):
        """Delete this language_pack."""
        handler = lp_handler.LanguagePackHandler(
            pecan.request.security_context)
        return handler.delete(self._id)


class LanguagePacksController(rest.RestController):
    """Manages operations on the language packs collection."""

    @pecan.expose()
    def _lookup(self, language_pack_id, *remainder):
        if remainder and not remainder[-1]:
            remainder = remainder[:-1]
        return LanguagePackController(language_pack_id), remainder

    @exception.wrap_controller_exception
    @wsme_pecan.wsexpose(lp.LanguagePack, body=lp.LanguagePack,
                         status_code=201)
    def post(self, data):
        """Create a new language_pack."""
        handler = lp_handler.LanguagePackHandler(
            pecan.request.security_context)
        return lp.LanguagePack.from_db_model(
            handler.create(data.as_dict(objects.registry.LanguagePack)),
            pecan.request.host_url)

    @exception.wrap_controller_exception
    @wsme_pecan.wsexpose([lp.LanguagePack])
    def get_all(self):
        """Return all language_packs, based on the query provided."""
        handler = lp_handler.LanguagePackHandler(
            pecan.request.security_context)
        return [lp.LanguagePack.from_db_model(langpack,
                pecan.request.host_url)
                for langpack in handler.get_all()]
