# Copyright 2014 - Rackspace Hosting
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

from solum.objects import base


class Image(base.CrudMixin):
    # Version 1.0: Initial version
    VERSION = '1.0'


class ImageList(list, base.CrudListMixin):
    """List of images."""


class States(object):
    QUEUED = 'QUEUED'
    BUILDING = 'BUILDING'
    ERROR = 'ERROR'
    READY = 'READY'

    @classmethod
    def as_dict(cls):
        return dict((k, v) for k, v in cls.__dict__.items()
                    if k[:2] != '__' and k not in ('values', 'as_dict'))

    @classmethod
    def values(cls):
        return cls.as_dict().values()
