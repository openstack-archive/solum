# Copyright 2015 - Rackspace Hosting
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

import datetime
import functools
import re
import shutil
import subprocess
import time
import types


def retry(fun):
    """Decorator to retry a call."""
    @functools.wraps(fun)
    def _wrapper(*args, **kwargs):
        max_retries = kwargs.pop('max_retries', 2)
        expected = kwargs.pop('expected_ret_code', 0)

        actual_ret = None
        for tries in range(max_retries):
            try:
                actual_ret = fun(*args, **kwargs)
                if expected == actual_ret:
                    return actual_ret
            except Exception:
                if tries + 1 >= max_retries:
                    raise

            time.sleep(1)
        return actual_ret
    return _wrapper


def is_git_sha(revision):
    return re.match(r'^([a-f0-9]{40})$', revision)


def timestamp():
    return datetime.datetime.utcnow().strftime('%Y%m%dt%H%M%S%f')


def rm_tree(directory):
    shutil.rmtree(directory)


class Shell(object):
    """Helper methods to run shell commands."""

    @classmethod
    def run(cls, args, timeout=None):
        if timeout:
            prefix = ['timeout', '--signal=SIGKILL', str(timeout)]
            if isinstance(args, types.StringTypes):
                args = prefix.append(args)
            elif isinstance(args, list):
                args = prefix.extend(args)

        return subprocess.call(args)
