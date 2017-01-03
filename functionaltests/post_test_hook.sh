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

# This script is executed inside post_test_hook function in devstack gate.

# Install packages from test-requirements.txt

sudo pip install -r /opt/stack/new/solum/test-requirements.txt

sudo pip install -U tempest-lib

sudo pip freeze

# Generate tempest.conf file
TEMPEST_BASE=/opt/stack/new/tempest/
cd $TEMPEST_BASE
sudo tox -egenconfig
sudo mkdir -p /etc/tempest
sudo cp $TEMPEST_BASE/etc/tempest.conf.sample /etc/tempest/tempest.conf

# Set test parameters
sudo sed -i s'/#auth_version = <None>/auth_version = v2/'g /etc/tempest/tempest.conf
sudo sed -i s'/#admin_project_name = <None>/admin_project_name = service/'g /etc/tempest/tempest.conf
sudo sed -i s'/#admin_password = <None>/admin_password = secretadmin/'g /etc/tempest/tempest.conf
sudo sed -i s'/#admin_username = <None>/admin_username = solum/'g /etc/tempest/tempest.conf
sudo sed -i s'/#uri_v3 = <None>/uri_v3 = http\:\/\/127.0.0.1\:5000\/v3/'g /etc/tempest/tempest.conf
sudo sed -i s'/#uri = <None>/uri = http\:\/\/127.0.0.1\:5000\/v2.0\//'g /etc/tempest/tempest.conf

sudo more /etc/tempest/tempest.conf

cd /opt/stack/new/solum/functionaltests
sudo ./run_tests.sh
