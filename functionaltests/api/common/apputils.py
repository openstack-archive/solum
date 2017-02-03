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

import random
import string


def get_sample_data(languagepack=''):
    data = dict()
    s = string.lowercase
    data["name"] = "test_app" + ''.join(random.sample(s, 5))
    data["description"] = "descp"
    data["languagepack"] = languagepack
    data["trigger_actions"] = ["test", "build", "deploy"]
    data["ports"] = [80]

    source = {}
    source['repository'] = "https://github.com/a/b.git"
    source['revision'] = "master"
    data["source"] = source

    workflow = {}
    workflow["test_cmd"] = "./unit_tests.sh"
    workflow["run_cmd"] = "python app.py"
    data["workflow_config"] = workflow

    data["repo_token"] = 'abc'

    return data
