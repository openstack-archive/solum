#!/bin/bash
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

# Where tempest code lives
TEMPEST_DIR=${TEMPEST_DIR:-/opt/stack/new/tempest}

# Add tempest source tree to PYTHONPATH
export PYTHONPATH=$PYTHONPATH:$TEMPEST_DIR

pushd $TEMPEST_DIR
tox -evenv
source .tox/venv/bin/activate
pip install nose
nosetests -sv "$SOLUM_TEMPEST_PLUGIN_ROOT/solum_tempest_plugin"
deactivate
popd
