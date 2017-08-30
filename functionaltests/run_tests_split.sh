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

# How many seconds to wait for the API to be responding before giving up
API_RESPONDING_TIMEOUT=20
SERVICES=("solum-api" "solum-worker" "solum-conductor" "solum-deployer")
SOLUM_CONFIG="/etc/solum/solum.conf"
declare -A CONFIG_SECTIONS=(["api"]=9777)
SOLUM_TEMPEST_PLUGIN_ROOT=/opt/stack/new/solum-tempest-plugin

function check_api {
    local host=$1
    local port=$2
    if ! timeout ${API_RESPONDING_TIMEOUT} sh -c "while ! curl -s -o /dev/null http://$host:$port ; do sleep 1; done"; then
        echo "Failed to connect to API $host:$port within ${API_RESPONDING_TIMEOUT} seconds"
        exit 1
    fi
}

# Check if solum services are running
for s in ${SERVICES[*]}
do
    if [ ! `pgrep -f $s` ]; then
        echo "$s is not running"
        exit 1
    fi
done

for sec in ${!CONFIG_SECTIONS[*]}
do
    pt=${CONFIG_SECTIONS[$sec]}
    line=$(sed -ne "/^\[$sec\]/,/^\[.*\]/ { /^port[ \t]*=/ p; }" $SOLUM_CONFIG)
    if [ ! -z "${line#*=}" ]; then
        pt=${line#*=}
    fi
    hst="127.0.0.1"
    line=$(sed -ne "/^\[$sec\]/,/^\[.*\]/ { /^host[ \t]*=/ p; }" $SOLUM_CONFIG)
    if [ ! -z "${line#*=}" ]; then
        hst=${line#*=}
    fi

    check_api $hst $pt
done

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
