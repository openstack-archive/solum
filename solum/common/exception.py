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

import functools
import pecan
import sys

from keystoneclient import exceptions as keystone_exceptions
from oslo.config import cfg
import six
import wsme

from solum.common import safe_utils
from solum.openstack.common import excutils
from solum.openstack.common.gettextutils import _
from solum.openstack.common import log as logging


LOG = logging.getLogger(__name__)

exc_log_opts = [
    cfg.BoolOpt('fatal_exception_format_errors',
                default=False,
                help='make exception message format errors fatal')
]

CONF = cfg.CONF
CONF.register_opts(exc_log_opts)


def wrap_exception(notifier=None, publisher_id=None, event_type=None,
                   level=None):
    """This decorator wraps a method to catch any exceptions that may
    get thrown. It logs the exception as well as optionally sending
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
                        call_dict = safe_utils.getcallargs(f, *args, **kw)
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


def wrap_controller_exception(func):
    """This decorator wraps controllers method to manage wsme exceptions:
    a wsme ClientSideError is raised if a SolumException is thrown.
    """
    @functools.wraps(func)
    def wrapped(*args, **kw):
        try:
            return func(*args, **kw)
        except SolumException as excp:
            pecan.response.translatable_error = excp
            raise wsme.exc.ClientSideError(six.text_type(excp), excp.code)
    return wrapped


def wrap_keystone_exception(func):
    """This decorator wraps keystone exception by throwing Solum specific
    exceptions.
    """
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
            assert isinstance(self.msg_fmt, six.text_type)

        try:
            self.message = self.msg_fmt % kwargs
        except KeyError:
            #kwargs doesn't match a variable in the message
            #log the issue and the kwargs
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
        if six.PY3:
            return self.message
        return self.message.encode('utf-8')

    def __unicode__(self):
        return self.message


class ObjectNotFound(SolumException):
    msg_fmt = _("The %(name)s %(id)s could not be found.")


class ObjectNotUnique(SolumException):
    msg_fmt = _("The %(name)s already exists.")


class ResourceNotFound(ObjectNotFound):
    msg_fmt = _("The %(name)s resource %(id)s could not be found.")
    code = 404


class ResourceExists(ObjectNotUnique):
    msg_fmt = _("The %(name)s resource already exists.")
    code = 409


class BadRequest(SolumException):
    msg_fmt = _("The request is malformed. Reason: %(reason)s")
    code = 400


class NotImplemented(SolumException):
    msg_fmt = _("The requested operation is not implemented.")
    code = 501


class AuthorizationFailure(SolumException):
    msg_fmt = _("%(client)s connection failed. %(message)s")
