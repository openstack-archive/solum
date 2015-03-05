# Copyright 2014 - Rackspace Hosting
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Get tempUrl for DU stored in swift."""

import hashlib
import hmac
import sys
import time

if len(sys.argv) < 8:
    print('USAGE: python get-temp-url.py storage_host container'
          ' app_name account secret ttl protocol')
    sys.exit(1)

storage_host = sys.argv[1]
container = sys.argv[2]
app_name = sys.argv[3]
account = sys.argv[4]
secret = sys.argv[5]
ttl = sys.argv[6]
protocol = sys.argv[7]

method = 'GET'
expires = int(time.time() + int(ttl))

base = protocol + "://"
base += storage_host

path = '/v1'
path += "/" + account
path += "/" + container
path += "/" + app_name

hmac_body = '%s\n%s\n%s' % (method, expires, path)
sig = hmac.new(secret, hmac_body, hashlib.sha1).hexdigest()

print('%s%s?temp_url_sig=%s&temp_url_expires=%s' % (base, path, sig, expires))
