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

from oslo.config import cfg
import six

from solum.common import safe_utils
from solum.openstack.common import excutils
from solum.openstack.common.gettextutils import _
from solum.openstack.common import log as logging

LOG = logging.getLogger(__name__)

exc_log_opts = [
    cfg.BoolOpt('fatal_exception_format_errors',
                default=False,
                help='make exception message format errors fatal'),
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


class NotFound(SolumException):
    msg_fmt = _("The requested resource could not be found.")
    code = 404


class ApplicationNotFound(NotFound):
    msg_fmt = _("The application %(application_id)s could not be found.")


class PlanNotFound(NotFound):
    msg_fmt = _("The plan %(plan_id)s could not be found.")


class ResourceExists(SolumException):
    msg_fmt = _("The requested resource already exists.")
    code = 409


class ApplicationExists(ResourceExists):
    msg_fmt = _("This application already exists.")


class PlanExists(ResourceExists):
    msg_fmt = _("This plan already exists.")


class NotImplemented(SolumException):
    msg_fmt = _("The requested operation is not implemented.")
    code = 501
