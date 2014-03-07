# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sqlalchemy

from solum.objects import sensor as abstract
from solum.objects.sqlalchemy import models as sql


class Sensor(sql.Base, abstract.Sensor):
    """Represent an sensor in sqlalchemy."""

    __resource__ = 'sensors'
    __tablename__ = 'sensor'
    __table_args__ = sql.table_args()

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True,
                           autoincrement=True)
    uuid = sqlalchemy.Column(sqlalchemy.String(36))
    project_id = sqlalchemy.Column(sqlalchemy.String(36))
    user_id = sqlalchemy.Column(sqlalchemy.String(36))
    name = sqlalchemy.Column(sqlalchemy.String(255))
    sensor_type = sqlalchemy.Column(sqlalchemy.String(255))
    value = sqlalchemy.Column(sqlalchemy.String(255))
    timestamp = sqlalchemy.Column(sqlalchemy.DateTime)
    description = sqlalchemy.Column(sqlalchemy.String(255))
    documentation = sqlalchemy.Column(sqlalchemy.String(255))
    target_resource = sqlalchemy.Column(sqlalchemy.String(255))


class SensorList(abstract.SensorList):
    """Represent a list of sensors in sqlalchemy."""

    @classmethod
    def get_all(cls, context):
        return SensorList(sql.model_query(context, Sensor))
