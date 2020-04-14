# Copyright 2015 - Rackspace US, Inc.
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


import datetime

import wsme
from wsme import types as wtypes

from solum.api.controllers.v1.datamodel import types as api_types


class App(api_types.Base):
    """Representation of an App.

    The App is the primary resource managed by Solum.
    """
    # Inherited fields:
    # uri
    # uuid
    # name is overridden.
    # type
    # description
    # tags
    # project_id
    # user_id

    version = wtypes.wsattr(int)
    id = wtypes.text
    name = wtypes.text
    deleted = bool
    languagepack = wtypes.text
    stack_id = wtypes.text
    ports = api_types.MultiType(api_types.PortType,
                                [api_types.PortType],
                                {wtypes.text: api_types.PortType})
    source = wtypes.DictType(wtypes.text, api_types.MultiType(
        wtypes.text,
        int,
        bool,
        float))
    workflow_config = {wtypes.text: wtypes.text}
    trigger_uuid = wtypes.text
    trigger_actions = [wtypes.text]
    trigger_uri = wtypes.text
    trust_id = wtypes.text
    trust_user = wtypes.text
    app_url = wtypes.text
    status = wtypes.text
    repo_token = wtypes.text
    created_at = datetime.datetime
    updated_at = datetime.datetime
    raw_content = wtypes.text
    repo_token = wtypes.text
    scale_config = wtypes.DictType(
        wtypes.text,
        wtypes.DictType(wtypes.text, wtypes.text))

    parameters = wtypes.DictType(
        wtypes.text,
        wtypes.DictType(wtypes.text,
                        api_types.MultiType(
                            wtypes.text,
                            int,
                            bool,
                            float)))

    def __init__(self, *args, **kwargs):
        super(App, self).__init__(*args, **kwargs)

    @classmethod
    def sample(cls):
        return cls(
            name="sampleapp",
            description="sample app",
            )

    @classmethod
    def from_db_model(cls, m, host_url):

        json = m.as_dict()
        json['type'] = m.__tablename__
        json['uri'] = '%s/v1/apps/%s' % (host_url, m.id)
        json['trigger_uri'] = ('%s/v1/triggers/%s' %
                               (host_url, m.trigger_uuid))
        return cls(**(json))

    def as_dict(self, db_model):
        attrs = [
            'name',
            'id',
            'description',
            'languagepack',
            'project_id',
            'user_id',
            'deleted',
            'source',
            'ports',
            'trigger_actions',
            'workflow_config',
            'stack_id',
            'raw_content',
            'repo_token'
            ]
        base = super(App, self).as_dict(db_model)

        if self.parameters is not wsme.Unset:
            base.update({'parameters': self.parameters})

        for a in attrs:
            if getattr(self, a) is wsme.Unset:
                continue
            if getattr(self, a) is None:
                continue
            base[a] = getattr(self, a)
        return base
