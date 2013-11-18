#!/bin/sh
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

TEMPDIR=`mktemp -d`
CFGFILE=solum.conf.sample
tools/config/generate_sample.sh -b ./ -p solum -o $TEMPDIR
if ! diff $TEMPDIR/$CFGFILE etc/solum/$CFGFILE
then
    echo "E: solum.conf.sample is not up to date, please run tools/config/generate_sample.sh"
    exit 42
fi
