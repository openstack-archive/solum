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

"""
test_solum
----------------------------------

Tests for `solum` module.
"""
from oslo_log import log as logging

from solum.tests import base

LOG = logging.getLogger(__name__)


class TestSolum(base.BaseTestCase):

    def test_can_use_oslo_logging(self):
        # Just showing that we can import and use logging
        LOG.info('Nothing to see here.')
