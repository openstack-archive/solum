# Copyright 2014 - Rackspace US, Inc.
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

import uuid

import sqlalchemy as sa
from sqlalchemy import orm

from solum.common import exception
from solum.objects import compiler_versions as abs_cv
from solum.objects import language_pack as abstract
from solum.objects import os_platform as abs_op
from solum.objects.sqlalchemy import models as sql


class LanguagePack(sql.Base, abstract.LanguagePack):
    """Represent a language pack in sqlalchemy."""

    __resource__ = 'language_packs'
    __tablename__ = 'language_pack'
    __table_args__ = sql.table_args()

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    uuid = sa.Column(sa.String(36), nullable=False)
    name = sa.Column(sa.String(100))
    description = sa.Column(sa.String(255))
    project_id = sa.Column(sa.String(36))
    user_id = sa.Column(sa.String(36))
    language_implementation = sa.Column(sa.String(100))
    language_pack_type = sa.Column(sa.String(100))
    tags = sa.Column(sa.Text)
    compiler_versions = orm.relationship("CompilerVersions",
                                         backref=__tablename__,
                                         lazy="joined")
    os_platform = orm.relationship("OSPlatform",
                                   backref=__tablename__,
                                   lazy="joined",
                                   uselist=False)
    attr_blob = sa.Column(sql.JSONEncodedDict(255))

    def destroy(self, context):
        session = sql.Base.get_session()
        with session.begin(subtransactions=True):
            for compiler_version in self.compiler_versions:
                compiler_version.destroy(context)
            if self.os_platform:
                self.os_platform.destroy(context)
            session.query(self.__class__).filter_by(id=self.id).delete()

    def _non_updatable_fields(self):
        return super(LanguagePack, self)._non_updatable_fields().union(
            set(('compiler_versions', 'os_platform')))

    def as_dict(self):
        d = super(LanguagePack, self).as_dict()
        if self.compiler_versions:
            d['compiler_versions'] = []
            for comp_version in self.compiler_versions:
                d['compiler_versions'].append(comp_version.version)
        if self.os_platform:
            d['os_platform'] = {'OS': self.os_platform.os,
                                'version': self.os_platform.version}
        return d

    def _update_compiler_versions(self, data):
        api_versions = data.get('compiler_versions', [])
        obj_to_remove = []
        existing_versions = []
        for obj_db in self.compiler_versions:
            if obj_db.version not in api_versions:
                obj_to_remove.append(obj_db)
            else:
                existing_versions.append(obj_db.version)
        for cv_to_remove in obj_to_remove:
            self.compiler_versions.remove(cv_to_remove)
            #TODO(julienvey) find a way to pass the context
            cv_to_remove.destroy(None)
        for comp_version in set(api_versions):
            if comp_version not in existing_versions:
                cv = CompilerVersions()
                cv.version = comp_version
                cv.uuid = uuid.uuid4()
                self.compiler_versions.append(cv)

    def _update_os_platform(self, data):
        api_os_platform = data.get('os_platform', None)
        if not api_os_platform:
            if self.os_platform:
                #TODO(julienvey) find a way to pass the context
                self.os_platform.destroy(None)
                self.os_platform = None
        elif 'OS' in api_os_platform and 'version' in api_os_platform:
            if not self.os_platform:
                self.os_platform = OSPlatform()
                self.os_platform.uuid = uuid.uuid4()
            self.os_platform.os = api_os_platform['OS']
            self.os_platform.version = api_os_platform['version']
        else:
            raise exception.BadRequest(reason="os_platform does not contain"
                                              " OS and version attributes")

    def update(self, data):
        super(LanguagePack, self).update(data)
        self._update_compiler_versions(data)
        self._update_os_platform(data)


class CompilerVersions(sql.Base, abs_cv.CompilerVersions):

    __tablename__ = 'compiler_versions'
    __table_args__ = sql.table_args()

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    uuid = sa.Column(sa.String(36), nullable=False)
    version = sa.Column(sa.String(36), nullable=False)
    language_pack_id = sa.Column(sa.Integer, sa.ForeignKey('language_pack.id'),
                                 nullable=False)


class OSPlatform(sql.Base, abs_op.OSPlatform):

    __tablename__ = 'os_platform'
    __table_args__ = sql.table_args()

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    uuid = sa.Column(sa.String(36), nullable=False)
    os = sa.Column(sa.String(36), nullable=False)
    version = sa.Column(sa.String(36), nullable=False)
    language_pack_id = sa.Column(sa.Integer, sa.ForeignKey('language_pack.id'),
                                 nullable=False)


class LanguagePackList(abstract.LanguagePackList):
    """Represent a list of language packs in sqlalchemy."""

    @classmethod
    def get_all(cls, context):
        return LanguagePackList(sql.model_query(context, LanguagePack))
