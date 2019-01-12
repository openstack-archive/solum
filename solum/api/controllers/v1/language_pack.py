# Copyright 2014 - Rackspace Hosting
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

import re

import pecan
from pecan import rest
import wsmeext.pecan as wsme_pecan

from solum.api.controllers.v1.datamodel import language_pack
import solum.api.controllers.v1.userlog as userlog_controller
from solum.api.handlers import language_pack_handler
from solum.common import exception
from solum.common import policy
from solum import objects


class LanguagePackController(rest.RestController):
    """Manages operations on a single languagepack."""

    def __init__(self, lp_id):
        super(LanguagePackController, self).__init__()
        self._id = lp_id

    @pecan.expose()
    def _lookup(self, primary_key, *remainder):
        if remainder and not remainder[-1]:
            remainder = remainder[:-1]
        if primary_key == 'logs':
            logs = userlog_controller.UserlogsController(self._id)
            return logs, remainder

    @exception.wrap_pecan_controller_exception
    @wsme_pecan.wsexpose(language_pack.LanguagePack)
    def get(self):
        """Return a languagepack."""
        policy.check('show_languagepack',
                     pecan.request.security_context)
        handler = language_pack_handler.LanguagePackHandler(
            pecan.request.security_context)

        host_url = pecan.request.application_url.rstrip('/')
        return language_pack.LanguagePack.from_db_model(handler.get(self._id),
                                                        host_url)

    @exception.wrap_pecan_controller_exception
    @wsme_pecan.wsexpose(status_code=204)
    def delete(self):
        """Delete a languagepack."""
        policy.check('delete_languagepack',
                     pecan.request.security_context)
        handler = language_pack_handler.LanguagePackHandler(
            pecan.request.security_context)
        return handler.delete(self._id)


class LanguagePacksController(rest.RestController):
    """Manages operations on the languagepack collection."""

    @pecan.expose()
    def _lookup(self, lp_id, *remainder):
        if remainder and not remainder[-1]:
            remainder = remainder[:-1]
        return LanguagePackController(lp_id), remainder

    @exception.wrap_pecan_controller_exception
    @wsme_pecan.wsexpose(language_pack.LanguagePack,
                         body=language_pack.LanguagePack,
                         status_code=201)
    def post(self, data):
        """Create a new languagepack."""
        policy.check('create_languagepack',
                     pecan.request.security_context)
        handler = language_pack_handler.LanguagePackHandler(
            pecan.request.security_context)
        host_url = pecan.request.application_url.rstrip('/')

        msg = ("Languagepack name must be 1-100 characters long, only contain "
               "a-z,0-9,-,_ and start with an alphabet character.")
        if not data.name or not data.name[0].isalpha():
            raise exception.BadRequest(reason=msg)

        try:
            re.match(r'^([a-z0-9-_]{1,100})$', data.name).group(0)
        except AttributeError:
            raise exception.BadRequest(reason=msg)

        return language_pack.LanguagePack.from_db_model(
            handler.create(data.as_dict(objects.registry.Image),
                           data.lp_metadata, data.lp_params), host_url)

    @exception.wrap_pecan_controller_exception
    @wsme_pecan.wsexpose([language_pack.LanguagePack])
    def get_all(self):
        """Return all languagepacks, based on the query provided."""
        policy.check('get_languagepacks',
                     pecan.request.security_context)
        handler = language_pack_handler.LanguagePackHandler(
            pecan.request.security_context)
        host_url = pecan.request.application_url.rstrip('/')
        return [language_pack.LanguagePack.from_db_model(img, host_url)
                for img in handler.get_all()]
