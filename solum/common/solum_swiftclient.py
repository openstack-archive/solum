# Copyright 2015 - Rackspace Hosting.
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

import errno
import os

from http import client as http_client
from oslo_log import log as logging
from swiftclient import exceptions as swiftexp

from solum.common import clients
from solum.common import exception as exc


CHUNKSIZE = 65536
TOTAL_RETRIES = 3
Gi = 1024 * 1024 * 1000
LARGE_OBJECT_SIZE = 5 * Gi

LOG = logging.getLogger(__name__)


class SwiftClient(object):
    """Swift client wrapper so we can encapsulate logic in one place.

       Most of the code in this class are borrowed from
       glance_store._drivers.swift.store.
       """

    def __init__(self, context):
        self.context = context

    def _get_swift_client(self):
        # Create a new non-cached swift client/connection
        return clients.OpenStackClients(self.context).swift()

    def _get_file_size(self, file_obj):
        # Analyze file-like object and attempt to determine its size.

        if (hasattr(file_obj, 'seek') and hasattr(file_obj, 'tell') and
                file_obj.seekable()):
            try:
                curr = file_obj.tell()
                file_obj.seek(0, os.SEEK_END)
                size = file_obj.tell()
                file_obj.seek(curr)
                return size
            except IOError as e:
                if e.errno == errno.ESPIPE:
                    # Illegal seek. This means the file object
                    # is a pipe (e.g. the user is trying
                    # to pipe image data to the client,
                    # echo testdata | bin/glance add blah...), or
                    # that file object is empty, or that a file-like
                    # object which doesn't support 'seek/tell' has
                    # been supplied.
                    return 0
                else:
                    raise
        else:
            return 0

    def _get_object(self, container, name, start_byte=None):
        connection = self._get_swift_client()
        headers = {}
        if start_byte is not None:
            bytes_range = 'bytes=%d-' % start_byte
            headers = {'Range': bytes_range}

        try:
            resp_headers, resp_body = connection.get_object(
                container=container, obj=name, resp_chunk_size=CHUNKSIZE,
                headers=headers)
        except swiftexp.ClientException as e:
            if e.http_status == http_client.NOT_FOUND:
                LOG.debug("Swift could not find object %s." % name)
            raise

        return (resp_headers, resp_body)

    def _retry_iter(self, resp_iter, length, container, name):
        length = length if length else (resp_iter.len
                                        if hasattr(resp_iter, 'len') else 0)
        retries = 0
        bytes_read = 0

        while retries <= TOTAL_RETRIES:
            try:
                for chunk in resp_iter:
                    yield chunk
                    bytes_read += len(chunk)
            except swiftexp.ClientException as e:
                LOG.debug("Swift exception %s" % e.__class__.__name__)
                pass

            if bytes_read == length:
                break
            else:
                if retries == TOTAL_RETRIES:
                    raise exc.MaxRetryReached
                else:
                    retries += 1
                    # NOTE(james_li): Need a new swift connection to do
                    # a range request for the same object
                    (_resp_headers, resp_iter) = self._get_object(
                        container, name, start_byte=bytes_read)

    def upload(self, path, container, name):
        connection = self._get_swift_client()
        with open(path, 'rb') as local_file:
            size = self._get_file_size(local_file)
            if size > 0 and size < LARGE_OBJECT_SIZE:
                connection.put_container(container)
                connection.put_object(container, name, local_file,
                                      content_length=size)
            else:
                raise exc.InvalidObjectSizeError

    def download(self, path, container, name):
        (resp_headers, resp_data) = self._get_object(container, name)
        length = int(resp_headers.get('content-length', 0))
        data_iter = self._retry_iter(resp_data, length, container, name)

        with open(path, 'wb') as local_file:
            for chunk in data_iter:
                local_file.write(chunk)
            local_file.flush()

    def delete_object(self, container, filename):
        swift = self._get_swift_client()
        try:
            swift.delete_object(container, filename)
        except swiftexp.ClientException as e:
            if e.http_status == http_client.NOT_FOUND:
                LOG.debug("Swift could not find object %s." % filename)
                pass
            else:
                raise

    def delete_container(self, container):
        swift = self._get_swift_client()
        swift.delete_container(container)
