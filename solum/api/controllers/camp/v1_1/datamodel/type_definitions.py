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

import copy

import pecan
from pecan import core

from solum.api.controllers.camp.v1_1.datamodel import types as camp_types
from solum.api.controllers.camp.v1_1 import uris
from solum.api.controllers import common_types
from solum.api.controllers.v1.datamodel import types as api_types
from solum.api.handlers.camp import attribute_definition_handler


class AttributeLink(common_types.Link):
    """CAMP v1.1 AttributeLink

    Links type_definition resources to attribute_definition resources.
    """

    required = camp_types.BooleanType
    """The value of the required attribute determines if the attribute defined
    by the attribute_definition resource referenced by this AttributeLink is
    required for resources of the type defined by the containing
    type_definition resource.
    """

    mutable = camp_types.BooleanType
    """The value of the mutable attribute determines if the attribute defined
    by the attribute_definition resource referenced by this AttributeLink is
    mutable for resources of the type defined by the containing
    type_definition resource.
    """

    consumer_mutable = camp_types.BooleanType
    """The value of the consumer_mutable attribute determines if the attribute
    defined by the attribute_definition resource referenced by this
    AttributeLink is writable by Consumers for resources of the type defined
    by the containing type_definition resource.
    """

    @classmethod
    def from_json(cls, dct):
        ret_val = cls()
        for key, value in dct.items():
            if hasattr(ret_val, key):
                setattr(ret_val, key, value)
        return ret_val

    def fix_uris(self, host_url):
        handler = (attribute_definition_handler.
                   AttributeDefinitionHandler(pecan.request.security_context))
        raw_def = handler.get(self.href)
        if not raw_def:
            core.abort(404,
                       'no attribute definition_link for %s' %
                       self.href)
        self.target_name = raw_def.name
        self.href = uris.ATTRIBUTE_DEF_URI_STR % (host_url, self.href)


class TypeDefinition(api_types.Base):
    """CAMP v1.1 type_definition resource."""

    documentation = common_types.Uri
    """This attribute contains a URI that points to the documentation for the
     resource type; required. not mutable."""

    inherits_from = [common_types.Link]
    """Each Link in this array points to a type_definition resource that the
     described resource's type inherits from; not required, not mutable."""

    attribute_definition_links = [AttributeLink]
    """Each AttributeLink in this array references an attribute_definition
     resource. Each of these attribute_definition resources represents an
     attribute of the type described by this type_definition resource;
     required, not mutable."""

    def __init__(self, **kwds):
        super(TypeDefinition, self).__init__(**kwds)

    @classmethod
    def from_json(cls, dct):
        ret_val = cls()
        for key, value in dct.items():
            if key == 'inherits_from':
                inherit_links = []
                for l_dict in value:
                    link = common_types.Link(href=l_dict['href'],
                                             target_name=l_dict['target_name'])
                    inherit_links.append(link)
                setattr(ret_val, 'inherits_from', inherit_links)
            elif key == 'attribute_definition_links':
                ad_links = []
                for ad_dct in value:
                    ad_link = AttributeLink.from_json(ad_dct)
                    ad_links.append(ad_link)
                setattr(ret_val, 'attribute_definition_links', ad_links)
            elif hasattr(ret_val, key):
                setattr(ret_val, key, value)
            else:
                core.abort(500, 'internal metadata is incorrect')
        return ret_val

    def fix_uris(self, host_url):
        """Update URIs to reflect a host URL."""
        ret_val = copy.deepcopy(self)
        ret_val.uri = uris.TYPE_DEF_URI_STR % (host_url, ret_val.uri)

        # 'inherits_from' is optional
        if ret_val.inherits_from:
            for ih_link in ret_val.inherits_from:
                ih_link.href = uris.TYPE_DEF_URI_STR % (host_url, ih_link.href)

        # 'attribute_definition_links' is required
        for ad_link in ret_val.attribute_definition_links:
            ad_link.fix_uris(host_url)

        return ret_val


class TypeDefinitions(api_types.Base):
    """CAMP v1.1 type_definitions resource."""

    type_definition_links = [common_types.Link]
    """This attribute contains Links to type_definition resources that contain
    information about resource types supported by the Platform.
    """

    def __init__(self, **kwds):
        super(TypeDefinitions, self).__init__(**kwds)
