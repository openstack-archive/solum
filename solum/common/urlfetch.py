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

from oslo_log import log as logging
import requests
from requests import exceptions
import urllib

from solum.i18n import _

LOG = logging.getLogger(__name__)


def get(url, max_size, chunk_size=None, allowed_schemes=('http', 'https')):
    """Get the data at the specified URL.

    The URL must use the http: or https: schemes.
    The file: scheme is also supported if you override
    the allowed_schemes argument.
    The max_size represents the total max byte of your file.
    The chunk_size is by default set at max_size, it represents the size
    of your chunk.
    Raise an IOError if getting the data fails.
    Raise an IOError if max_size is less than 1.
    Raise an IOError if chunk_size is less than 1.
    """

    LOG.info(_('Fetching data from %s') % url)

    components = urllib.parse.urlparse(url)

    if components.scheme not in allowed_schemes:
        raise IOError(_('Invalid URL scheme %s') % components.scheme)

    if chunk_size is None:
        chunk_size = max_size
    if max_size < 1:
        raise IOError("max_size should be greater than 0")
    if chunk_size < 1:
        raise IOError("chunk_size should be greater than 0")

    if components.scheme == 'file':
        try:
            return urllib.request.urlopen(url).read()
        except urllib.error.URLError as uex:
            raise IOError(_('Failed to read file: %s') % str(uex))

    try:
        resp = requests.get(url, stream=True)
        resp.raise_for_status()

        # We cannot use resp.text here because it would download the
        # entire file, and a large enough file would bring down the
        # engine.  The 'Content-Length' header could be faked, so it's
        # necessary to download the content in chunks to until
        # max_size is reached.  The chunk_size we use needs
        # to balance CPU-intensive string concatenation with accuracy
        # (eg. it's possible to fetch 1000 bytes greater than
        # max_size with a chunk_size of 1000).
        reader = resp.iter_content(chunk_size=chunk_size)
        result = ""
        for chunk in reader:
            result += chunk
            if len(result) > max_size:
                raise IOError("File exceeds maximum allowed size (%s "
                              "bytes)" % max_size)
        return result

    except exceptions.RequestException as ex:
        raise IOError(_('Failed to retrieve file: %s') % str(ex))
