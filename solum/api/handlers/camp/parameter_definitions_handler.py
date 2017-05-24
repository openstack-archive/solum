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


from solum.api.controllers.camp.v1_1.datamodel import (parameter_definitions
                                                       as pd)
from solum.api.handlers import handler


DEPLOY_PARAM_DESCRIPTION = ("Solum CAMP API definitions of the 'pdp_uri', "
                            "'plan_uri', 'pdp_file', and 'plan_file' "
                            "parameters.")

DEPLOY_PARAM_LINKS = [
    pd.ParameterDefinitionLink(href='pdp_uri_param',
                               target_name='pdp_uri',
                               required=False),
    pd.ParameterDefinitionLink(href='plan_uri_param',
                               target_name='plan_uri',
                               required=False),
    pd.ParameterDefinitionLink(href='pdp_file_param',
                               target_name="pdp_file",
                               required=False),
    pd.ParameterDefinitionLink(href='plan_file_param',
                               target_name="plan_file",
                               required=False)
]

NDT_PARAM_DESCRIPTION = ("Solum CAMP API definitions of the 'name', "
                         "'description', and 'tag' parameters.")

NDT_PARAM_LINKS = [
    pd.ParameterDefinitionLink(href='name_param',
                               target_name='name',
                               required=False),
    pd.ParameterDefinitionLink(href='description_param',
                               target_name='description',
                               required=False),
    pd.ParameterDefinitionLink(href='tags_param',
                               target_name='tags',
                               required=False)
]

GLOBAL_PARAM_DEFS = {
    'deploy_params':
        pd.ParameterDefinitions(uri='deploy_params',
                                name='Solum_CAMP_deploy_parameters',
                                type='parameter_definitions',
                                description=DEPLOY_PARAM_DESCRIPTION,
                                parameter_definition_links=DEPLOY_PARAM_LINKS),
    'ndt_params':
        pd.ParameterDefinitions(uri='ndt_params',
                                name='Solum_CAMP_NDT_parameters',
                                type='parameter_definitions',
                                description=NDT_PARAM_DESCRIPTION,
                                parameter_definition_links=NDT_PARAM_LINKS)
}


class ParameterDefinitionsHandler(handler.Handler):

    def get(self, path):
        if path in GLOBAL_PARAM_DEFS:
            return GLOBAL_PARAM_DEFS[path]
