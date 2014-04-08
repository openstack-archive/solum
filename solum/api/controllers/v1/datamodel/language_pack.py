# Copyright 2014 - Rackspace
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

from wsme import types as wtypes

from solum.api.controllers.v1.datamodel import types as api_types


class BuildTool(wtypes.Base):
    """A build tool representation."""

    type = str
    "The type of the build tool."

    version = wtypes.text
    "Version of the build tool."

    @classmethod
    def sample(cls):
        return cls(type=('ant'), version='1.7')


class LanguagePack(api_types.Base):
    """Representation of a language pack.

    When a user creates an application, he specifies the language pack
    to be used. The language pack is responsible for building the application
    and producing an artifact for deployment.

    For a complete list of language pack attributes please
    refer: https://etherpad.openstack.org/p/Solum-Language-pack-json-format
    """

    language_pack_name = wtypes.text
    """Name of the language pack."""

    language_pack_type = wtypes.text
    """Type of the language pack. Identifies the language supported by the
    language pack. This attribute value will use the
    org.openstack.solum namespace.
    """

    language_pack_id = wtypes.text
    """Identifier of the language pack image as returned by glance."""

    compiler_versions = [wtypes.text]
    """List of all the compiler versions supported by the language pack.
    Example: For a java language pack supporting Java versions 1.4 to 1.7,
    version = ['1.4', '1.6', '1.7']
    """

    runtime_versions = [wtypes.text]
    """List of all runtime versions supported by the language pack.
    Runtime version can be different than compiler version.
    Example: An application can be compiled with java 1.7 but it should
    run in java 1.6 as it is backward compatible.
    """

    language_implementation = wtypes.text
    """Actual language implementation supported by the language pack.
    Example: In case of java it might be 'Sun' or 'openJava'
    In case of C++ it can be 'gcc' or 'icc' or 'microsoft'.
    """

    build_tool_chain = [BuildTool]
    """Toolchain available in the language pack.
    Example: For a java language pack which supports Ant and Maven,
    build_tool_chain = ["{type:ant,version:1.7}","{type:maven,version:1.2}"]
    """

    os_platform = {str: wtypes.text}
    """OS and its version used by the language pack.
    This attribute identifies the base image of the language pack.
    """

    attributes = {str: wtypes.text}
    """Additional section attributes will be used to expose custom
    attributes designed by language pack creator.
    """

    @classmethod
    def sample(cls):
        return cls(uri='http://example.com/v1/language_packs/123456abcdef',
                   name='language-pack',
                   type='service',
                   description=('Base Java LP with Java version 1.4-1.7.'
                                ' Supports ant, maven.'),
                   project_id='1dae5a09ef2b4d8cbf3594b0eb4f6b94',
                   user_id='55f41cf46df74320b9486a35f5d28a11',
                   tags=['group_xyz'],
                   language_pack_name='java-1.4-1.7',
                   language_pack_type='org.openstack.solum.Java',
                   language_pack_id='123456789abcdef',
                   compiler_versions=['1.4', '1.6', '1.7'],
                   runtime_versions=['1.4', '1.6', '1.7'],
                   language_implementation='Sun',
                   build_tool_chain=[BuildTool(type='ant', version='1.7'),
                        BuildTool(type='maven', version='1.2')],
                   os_platform={'OS': 'Ubuntu', 'version': '12.04'},
                   attributes={'optional_attr1': 'value',
                               'admin_email': 'someadmin@somewhere.com'},
                   )
