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

# This script is executed inside pre_test_hook function in devstack gate.

DEVSTACK_BASE=/opt/stack/new/devstack
DEVSTACK_GATE=/opt/stack/new/devstack-gate

# Install solum devstack integration
SOLUM_BASE=/opt/stack/new/solum/contrib/devstack
cp $SOLUM_BASE/lib/* $DEVSTACK_BASE/lib
cp $SOLUM_BASE/extras.d/* $DEVSTACK_BASE/extras.d

# TODO(ravips): Workaround until barbican, mistral gets into devstack
# Allow devstack to do git clone when directory doesn't exist
sed -e 's/ERROR_ON_CLONE=True/ERROR_ON_CLONE=False/' -i $DEVSTACK_GATE/devstack-vm-gate.sh
# Install barbican devstack integration
BARBICAN_BASE=/opt/stack/new/barbican/contrib/devstack
cp $BARBICAN_BASE/lib/* $DEVSTACK_BASE/lib
cp $BARBICAN_BASE/extras.d/* $DEVSTACK_BASE/extras.d
