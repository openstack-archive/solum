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

"""Solum base exception handling.

Includes decorator for re-raising Solum-type exceptions.

"""

import collections
import functools
import inspect
import sys

from keystoneclient import exceptions as keystone_exceptions
from oslo_config import cfg
from oslo_log import log as logging
from oslo_utils import excutils
from oslo_utils import uuidutils
import pecan
import wsme

from solum.i18n import _


LOG = logging.getLogger(__name__)

exc_log_opts = [
    cfg.BoolOpt('fatal_exception_format_errors',
                default=False,
                help='make exception message format errors fatal')
]


def list_opts():
    yield None, exc_log_opts


CONF = cfg.CONF
CONF.register_opts(exc_log_opts)


def wrap_exception(notifier=None, publisher_id=None, event_type=None,
                   level=None):
    """This decorator wraps a method to catch any exceptions.

    It logs the exception as well as optionally sending
    it to the notification system.
    """
    def inner(f):
        def wrapped(self, context, *args, **kw):
            # Don't store self or context in the payload, it now seems to
            # contain confidential information.
            try:
                return f(self, context, *args, **kw)
            except Exception as e:
                with excutils.save_and_reraise_exception():
                    if notifier:
                        call_dict = inspect.getcallargs(f, *args, **kw)
                        payload = dict(exception=e,
                                       private=dict(args=call_dict)
                                       )

                        # Use a temp vars so we don't shadow
                        # our outer definitions.
                        temp_level = level
                        if not temp_level:
                            temp_level = notifier.ERROR

                        temp_type = event_type
                        if not temp_type:
                            # If f has multiple decorators, they must use
                            # functools.wraps to ensure the name is
                            # propagated.
                            temp_type = f.__name__

                        notifier.notify(context, publisher_id, temp_type,
                                        temp_level, payload)

        return functools.wraps(f)(wrapped)
    return inner


OBFUSCATED_MSG = _('Your request could not be handled '
                   'because of a problem in the server. '
                   'Error Correlation id is: %s')


def wrap_controller_exception(func, func_server_error, func_client_error):
    """This decorator wraps controllers methods to handle exceptions:

    - if an unhandled Exception or a SolumException with an error code >=500
    is catched, raise a http 5xx ClientSideError and correlates it with a log
    message

    - if a SolumException is catched and its error code is <500, raise a http
    4xx and logs the exception in debug mode

    """
    @functools.wraps(func)
    def wrapped(*args, **kw):
        try:
            return func(*args, **kw)
        except Exception as excp:
            LOG.error(excp)
            http_error_code = 500
            if hasattr(excp, 'code'):
                http_error_code = excp.code

            if http_error_code >= 500:
                # log the error message with its associated
                # correlation id
                log_correlation_id = uuidutils.generate_uuid()
                LOG.error("%s:%s", log_correlation_id, str(excp))
                # raise a client error with an obfuscated message
                func_server_error(log_correlation_id, http_error_code)
            else:
                # raise a client error the original message
                func_client_error(excp, http_error_code)
    return wrapped


def wrap_wsme_controller_exception(func):
    """This decorator wraps wsme controllers to handle exceptions."""
    def _func_server_error(log_correlation_id, status_code):
        raise wsme.exc.ClientSideError(
            str(OBFUSCATED_MSG % log_correlation_id), status_code)

    def _func_client_error(excp, status_code):
        raise wsme.exc.ClientSideError(str(excp), status_code)

    return wrap_controller_exception(func,
                                     _func_server_error,
                                     _func_client_error)


def wrap_pecan_controller_exception(func):
    """This decorator wraps pecan controllers to handle exceptions."""
    def _func_server_error(log_correlation_id, status_code):
        pecan.response.status = status_code
        pecan.response.text = str(OBFUSCATED_MSG % log_correlation_id)
        # message body for errors is just a plain text message
        # The following code is functionally equivalent to calling:
        #
        #     pecan.override_template(None, "text/plain")
        #
        # We do it this way to work around a bug in our unit-test framework
        # in which the mocked request object isn't properly mocked in the pecan
        # core module (gilbert.plz@oracle.com)
        pecan.request.pecan['override_template'] = None
        pecan.request.pecan['override_content_type'] = 'text/plain'

    def _func_client_error(excp, status_code):
        pecan.response.status = status_code
        pecan.response.text = str(excp)

        # The following code is functionally equivalent to calling:
        #
        #     pecan.override_template(None, "text/plain")
        #
        # We do it this way to work around a bug in our unit-test framework
        # in which the mocked request object isn't properly mocked in the pecan
        # core module (gilbert.plz@oracle.com)
        pecan.request.pecan['override_template'] = None
        pecan.request.pecan['override_content_type'] = 'text/plain'

    return wrap_controller_exception(func,
                                     _func_server_error,
                                     _func_client_error)


def wrap_wsme_pecan_controller_exception(func):
    """Error handling for controllers decorated with wsmeext.pecan.wsexpose:

    Controllers wrapped with wsme_pecan.wsexpose don't throw
    exceptions but handle them internally. We need to intercept
    the response and mask potentially sensitive information.
    """

    @functools.wraps(func)
    def wrapped(*args, **kw):
        ret = func(*args, **kw)
        ismapping = isinstance(ret, collections.Mapping)
        if (pecan.response.status_code >= 500 and ismapping):

            log_correlation_id = uuidutils.generate_uuid()
            LOG.error("%s:%s", log_correlation_id, ret.get("faultstring",
                                                           "Unknown Error"))
            ret['faultstring'] = str(OBFUSCATED_MSG % log_correlation_id)
        return ret

    return wrapped


def wrap_keystone_exception(func):
    """Wrap keystone exceptions and throw Solum specific exceptions."""
    @functools.wraps(func)
    def wrapped(*args, **kw):
        try:
            return func(*args, **kw)
        except keystone_exceptions.AuthorizationFailure:
            raise AuthorizationFailure(
                client=func.__name__, message="reason: %s" % sys.exc_info()[1])
        except keystone_exceptions.ClientException:
            raise AuthorizationFailure(
                client=func.__name__,
                message="unexpected keystone client error occurred: %s"
                        % sys.exc_info()[1])
    return wrapped


class SolumException(Exception):
    """Base Solum Exception

    To correctly use this class, inherit from it and define
    a 'msg_fmt' property. That msg_fmt will get printf'd
    with the keyword arguments provided to the constructor.

    """
    message = _("An unknown exception occurred.")
    code = 500

    def __init__(self, **kwargs):
        self.kwargs = kwargs

        if CONF.fatal_exception_format_errors:
            assert isinstance(self.msg_fmt, str)

        try:
            self.message = self.msg_fmt % kwargs
        except KeyError:
            # kwargs doesn't match a variable in the message
            # log the issue and the kwargs
            LOG.exception(_('Exception in string format operation'),
                          extra=dict(
                              private=dict(
                                  msg=self.msg_fmt,
                                  args=kwargs
                                  )
                              )
                          )

            if CONF.fatal_exception_format_errors:
                raise

    def __str__(self):
        return self.message


class ResourceLimitExceeded(SolumException):
    msg_fmt = _("Resource limit exceeded. Reason: %(reason)s")


class BadRequest(SolumException):
    msg_fmt = _("The request is malformed. Reason: %(reason)s")
    code = 400


class ObjectNotFound(SolumException):
    msg_fmt = _("The %(name)s %(id)s could not be found.")


class ObjectNotUnique(SolumException):
    msg_fmt = _("The %(name)s already exists.")


class RequestForbidden(SolumException):
    msg_fmt = _("The request is forbidden. Reason: %(reason)s")
    code = 403


class ResourceNotFound(ObjectNotFound):
    msg_fmt = _("The %(name)s resource %(id)s could not be found.")
    code = 404


class ResourceExists(ObjectNotUnique):
    msg_fmt = _("The %(name)s resource already exists.")
    code = 409


class ResourceStillReferenced(SolumException):
    msg_fmt = _("The %(name)s resource cannot be deleted because one or more"
                " resources reference it.")
    code = 409


class UnsupportedMediaType(SolumException):
    msg_fmt = _("\'%(name)s\' is not a supported media type for the %(method)s"
                " method of this resource")
    code = 415


class Unprocessable(SolumException):
    msg_fmt = _("Server is incapable of processing the specified request.")
    code = 422


class PlanStillReferenced(ResourceStillReferenced):
    msg_fmt = _("Plan %(name)s cannot be deleted because one or more"
                " Assemblies reference it.")


class LPStillReferenced(ResourceStillReferenced):
    msg_fmt = _("Languagepack %(name)s cannot be deleted because one or more"
                " applications reference it.")


class NotImplemented(SolumException):
    msg_fmt = _("The requested operation is not implemented.")
    code = 501


class AuthorizationFailure(SolumException):
    msg_fmt = _("%(client)s connection failed. %(message)s")


class InvalidObjectSizeError(Exception):
    msg_fmt = _("Invalid object size.")


class MaxRetryReached(Exception):
    msg_fmt = _("Maximum retries has been reached.")
