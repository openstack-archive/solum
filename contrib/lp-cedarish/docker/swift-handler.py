# Copyright 2015 - Rackspace Hosting.
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

"""Swift Handler"""

import errno
import httplib
import os
import sys

import six
from swiftclient import client as swiftclient
from swiftclient import exceptions as swiftexp


CHUNKSIZE = 65536
TOTAL_RETRIES = 3
Gi = 1024 * 1024 * 1000
LARGE_OBJECT_SIZE = 5 * Gi


class InvalidObjectSizeError(Exception):
    pass


class MaxRetryReached(Exception):
    pass


def _get_swift_client(args):
    client_args = {
        'auth_version': '2.0',
        'preauthtoken': args['auth_token'],
        'preauthurl': args['storage_url'],
        'os_options': {'region_name': args['region_name']},
        }

    # swiftclient connection will retry the request
    # 5 times before failing
    return swiftclient.Connection(**client_args)


def _get_file_size(file_obj):
    # Analyze file-like object and attempt to determine its size.

    if (hasattr(file_obj, 'seek') and hasattr(file_obj, 'tell') and
            (six.PY2 or six.PY3 and file_obj.seekable())):
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
                print("Error getting file size")
                raise
    else:
        return 0


def _get_object(container, name, connection_args, start_byte=None):
    connection = _get_swift_client(connection_args)
    headers = {}
    if start_byte is not None:
        bytes_range = 'bytes=%d-' % start_byte
        headers = {'Range': bytes_range}

    try:
        resp_headers, resp_body = connection.get_object(
            container=container, obj=name, resp_chunk_size=CHUNKSIZE,
            headers=headers)
    except swiftexp.ClientException as e:
        if e.http_status == httplib.NOT_FOUND:
            print("Swift could not find object %s." % name)
        raise

    return (resp_headers, resp_body)


def _retry_iter(resp_iter, length, container, name, connection_args):
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
            print("Swift exception %s" % e.__class__.__name__)

        if bytes_read == length:
            break
        else:
            if retries == TOTAL_RETRIES:
                raise MaxRetryReached
            else:
                retries += 1
                print("Retrying Swift download")
                # NOTE(james_li): Need a new swift connection to do
                # a range request for the same object
                (_resp_headers, resp_iter) = _get_object(container, name,
                                                         connection_args,
                                                         start_byte=bytes_read)


def do_upload(path, container, name, connection_args):
    connection = _get_swift_client(connection_args)
    with open(path, 'rb') as local_file:
        size = _get_file_size(local_file)
        if size > 0 and size < LARGE_OBJECT_SIZE:
            connection.put_container(container)
            connection.put_object(container, name, local_file,
                                  content_length=size)
        else:
            print("Cannot upload a file with the size exceeding 5GB")
            raise InvalidObjectSizeError


def do_download(path, container, name, connection_args):
    (resp_headers, resp_data) = _get_object(container, name, connection_args)
    length = int(resp_headers.get('content-length', 0))
    data_iter = _retry_iter(resp_data, length, container, name,
                            connection_args)

    with open(path, 'wb') as local_file:
        for chunk in data_iter:
            local_file.write(chunk)
        local_file.flush()


def main():
    action_to_take = sys.argv[4]
    path = str(sys.argv[7])
    container = str(sys.argv[5])
    obj_name = str(sys.argv[6])
    connection_args = {'region_name': str(sys.argv[1]),
                       'auth_token': str(sys.argv[2]),
                       'storage_url': str(sys.argv[3])}

    if action_to_take == 'download':
        try:
            do_download(path, container, obj_name, connection_args)
            print("Finished swift download.")
            sys.exit(0)
        except Exception as e:
            print("Error download object, got %s" % e.__class__.__name__)
            sys.exit(1)
    elif action_to_take == 'upload':
        try:
            do_upload(path, container, obj_name, connection_args)
            print("Finished swift upload.")
            sys.exit(0)
        except Exception as e:
            print("Error upload object, got %s" % e.__class__.__name__)
            sys.exit(1)
    else:
        sys.exit(2)


if __name__ == '__main__':
    sys.exit(main())
