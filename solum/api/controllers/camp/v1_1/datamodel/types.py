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

import six
from wsme.rest import json
from wsme import types as wtypes


TRUE_STRINGS = ('true', 'True', 'TRUE')
FALSE_STRINGS = ('false', 'False', 'FALSE')


class BooleanType(wtypes.UserType):
    """A simple boolean type."""

    basetype = wtypes.text
    name = 'boolean'
    # FIXME(lucasagomes): When used with wsexpose decorator WSME will try
    # to get the name of the type by accessing it's __name__ attribute.
    # Remove this __name__ attribute once it's fixed in WSME.
    # https://bugs.launchpad.net/wsme/+bug/1265590
    __name__ = name

    @staticmethod
    def validate(value):
        if not isinstance(value, six.string_types):
            value = six.text_type(value)

        if value in TRUE_STRINGS:
            ret_val = True
        elif value in FALSE_STRINGS:
            ret_val = False
        else:
            acceptable = ', '.join(
                "'%s'" % s for s in sorted(TRUE_STRINGS + FALSE_STRINGS))
            msg = ("Unrecognized value '%(val)s', acceptable values are:"
                   " %(acceptable)s") % {'val': value,
                                         'acceptable': acceptable}
            raise ValueError(msg)

        return ret_val

    @staticmethod
    def frombasetype(value):
        if value is None:
            return None
        return BooleanType.validate(value)


@json.tojson.when_object(BooleanType)
def bool_tojson(datatype, value):
    if value:
        return 'true'
    else:
        return 'false'
