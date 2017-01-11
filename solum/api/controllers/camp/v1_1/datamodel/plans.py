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

import wsme
from wsme import types as wtypes

from solum.api.controllers import common_types
from solum.api.controllers.v1.datamodel import plan as solum_plan
from solum.api.controllers.v1.datamodel import types as api_types


class ServiceSpecification(solum_plan.ServiceReference):
    """CAMP v1.1 ServiceSpecification."""

    description = wtypes.text
    """A description of the specified service."""

    tags = [wtypes.text]
    """Tags for the specified service."""

    href = wtypes.text
    """Reference to a service resource that resolves the service described by
    this ServiceSpecification."""

    characteristics = [wtypes.DictType(wtypes.text, wtypes.text)]
    """An array of dictionaries that express the desired characteristics of
    any service that matches this specification."""

    def __init__(self, **kwargs):
        super(ServiceSpecification, self).__init__(**kwargs)


class RequirementSpecification(solum_plan.Requirement):
    """CAMP v1.1 RequirementSpecification."""

    fulfillment = api_types.MultiType(wtypes.text,
                                      ServiceSpecification)
    """Either a ServiceSpecification or a reference to a
    ServiceSpecification."""

    def __init__(self, **kwargs):
        if 'fulfillment' in kwargs:
            fulfill = kwargs.get('fulfillment')
            if type(fulfill) is not str:
                kwargs['fulfillment'] = ServiceSpecification(**fulfill)

        super(RequirementSpecification, self).__init__(**kwargs)


class ArtifactSpecification(solum_plan.Artifact):
    """CAMP v1.1 ArtifactSpecification."""

    description = wtypes.text
    """A description of the specified artifact."""

    tags = [wtypes.text]
    """Tags for the specified artifact."""

    requirements = [RequirementSpecification]
    """List of CAMP Requirement Specifications for the artifact."""

    def __init__(self, **kwargs):
        if 'requirements' in kwargs:
            kwargs['requirements'] = [RequirementSpecification(**rs)
                                      for rs in kwargs.get('requirements', [])]

        # Call our grandparent's (Base) constructor since we have already done
        # the work (creating objects from mappings) of our parent's (Artifact)
        # constructor and, if called, our parent's constructor will generate
        # an exception when it tries to create objects from these objects.
        wtypes.Base.__init__(self, **kwargs)


class Plan(solum_plan.Plan):
    """CAMP v1.1 plan resource."""

    camp_version = wsme.types.wsattr(wtypes.text, mandatory=True)
    """The value of this attribute expresses the version of the CAMP
    specification to which the Plan conforms."""

    origin = wtypes.text
    """The value of this attribute specifies the origin of the Plan."""

    artifacts = [ArtifactSpecification]
    """List of CAMP Artifact Specifications (see Section 4.3.3)."""

    services = [ServiceSpecification]
    """List of CAMP Service Specifications (see Section 4.3.6)."""

    def __init__(self, **kwargs):
        if 'artifacts' in kwargs:
            kwargs['artifacts'] = [ArtifactSpecification(**art)
                                   for art in kwargs.get('artifacts', [])]
        if 'services' in kwargs:
            kwargs['services'] = [ServiceSpecification(**sr)
                                  for sr in kwargs.get('services', [])]

        # Call our grandparent's (Base) constructor since we have already done
        # the work (creating objects from mappings) of our parent's (Plan)
        # constructor and, if called, our parent's constructor will generate
        # an exception when it tries to create objects from these objects.
        api_types.Base.__init__(self, **kwargs)


class Plans(api_types.Base):
    """CAMP v1.1 plans resource."""

    plan_links = [common_types.Link]
    """This attribute contains Links to the plan resources that represent the
    blueprints for applications deployed on the platform."""

    parameter_definitions_uri = common_types.Uri
    """The value of the parameter_definitions_uri attribute references a
    resource that contains links to parameter_definition resources that
    describe the parameters accepted by this resource on an HTTP POST
    method."""

    def __init__(self, **kwds):
        super(Plans, self).__init__(**kwds)
