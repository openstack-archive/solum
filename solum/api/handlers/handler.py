# Copyright 2013 - Rackspace
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

from solum.common import exception as solum_exception


class Handler(object):
    """The handler is responsible for fulfilling *one* request."""

    def __init__(self, context):
        super(Handler, self).__init__()
        self.context = context

    def get(self, id):
        """Return a resource."""
        excp = solum_exception.NotImplemented()
        raise excp

    def update(self, id, data):
        """Modify a resource."""
        excp = solum_exception.NotImplemented()
        raise excp

    def delete(self, id):
        """Delete a resource."""
        excp = solum_exception.NotImplemented()
        raise excp

    def create(self, data):
        """Create a new resource."""
        excp = solum_exception.NotImplemented()
        raise excp

    def get_all(self):
        """Return all resources, based on the query provided."""
        excp = solum_exception.NotImplemented()
        raise excp
