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

# The list below holds the keys corresponding to Oslo RequestContext keys
# which are acceptable for an authenticated user to view.  Everything else
# will be considered support-only data.  This list may be too restrictive and
# can be relaxed more as needed.  This is only used if import_context() is
# called.
_TRACE_USER_KEYS = ["user", "tenant"]
_TRACE_CONTEXT_IGNORE = ["auth_token", "trust_id"]


class TraceData(object):
    """This class holds trace data needed for logging.

    This class also provides a way to indicate the confidentiality of stored
    data.  This is useful for properly logging support or operator-only data
    in such a way that the backend log/notification filters have a single key
    to filter on.  It also provides a centralized location to add secure
    storage/cleanup algorithms.
    """
    def __init__(self):
        """Initialize class storage."""
        self.request_id = "<not set>"
        self._auto_clear = False
        self._user_data = {}
        self._support_data = {}

    def import_context(self, context):
        """Accept an Oslo RequestContext and fill in data automatically."""
        context_dict = context.to_dict()
        for key, val in context_dict.items():
            if key == "request_id":
                self.request_id = val
            elif key in _TRACE_USER_KEYS:
                self._user_data[key] = val
            elif key in _TRACE_CONTEXT_IGNORE:
                # these are just too big.
                continue
            else:
                self._support_data[key] = val

    def user_info(self, **kwargs):
        """Add data to user-visible storage."""
        self._user_data.update(kwargs)

    def support_info(self, **kwargs):
        """Add confidential data to support/operator-visible only storage."""
        self._support_data.update(kwargs)

    def clear(self):
        """Clear data regardless of confidential status.

        Note: The lightweight memory clearing below is certainly not what we
        want in the end.  It is just an initial/simple/portable way to do this
        for now.  It is only somewhat useful before garbage collection.
        """
        self.request_id = "<not set>"
        self._user_data = {}
        self._support_data = {}

    def to_dict(self):
        """Generate a dictionary for Oslo Log (requires 'request_id').

        Because this class initializes request_id to <not set> the log
        operation will succeed even if a UUID was not stored.
        """
        if self._auto_clear is not True:
            return ({"request_id": self.request_id,
                     "user_trace": self._user_data,
                     "support_trace": self._support_data})

        user_data = self._user_data.copy()
        support_data = self._support_data.copy()
        self.clear()
        return ({"request_id": self.request_id,
                 "user_trace": user_data,
                 "support_trace": support_data})

    @property
    def auto_clear(self):
        """_auto_clear getter."""
        return self._auto_clear

    @auto_clear.setter
    def auto_clear(self, value):
        """_auto_clear setter to enable assertion checks.

        When set to True, this class will automatically delete all trace data
        after the next Oslo log call (or a to_dict() call).  If the Oslo log
        call does not log any data (log levels preventing it for example) then
        the data is still deleted so care must be taken when using this.
        """
        assert isinstance(value, bool)
        self._auto_clear = value
