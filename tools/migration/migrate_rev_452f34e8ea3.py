#!/usr/bin/env python
# Copyright 2015 - Rackspace Hosting
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

'''
Data migration for alembic revision 452f34e8ea3
'''
import argparse
import getpass
import subprocess

import sqlalchemy as sa
from sqlalchemy.sql import text


DB_CONN = 'mysql://{user}:{password}@{host}/{db}?charset=utf8'
BACKUP_CMD = ('mysqldump --host={host} --user={user} --password={password}'
              ' --databases {db}')
DB_READ_SQL = 'select id, external_ref from image'
DB_UPDATE_SQL = ('update image set external_ref = :ref,'
                 ' docker_image_name = :name where id = :image_id')


def backup_db(db_host, db_user, db_password, db_name, bk_dir):
    cmd = BACKUP_CMD.format(host=db_host, user=db_user,
                            password=db_password, db=db_name)
    backup_file = bk_dir + '/' + 'arbor-db-452f34e8ea3.sql'

    print('===== Dumping solum db into %s' % backup_file)

    with open(backup_file, 'w') as bf:
        runbk = subprocess.Popen(cmd.split(), stdout=bf)
        returncode = runbk.wait()

    if returncode != 0:
        print('mysqldump failed, exit.')
        exit(1)


def update_db(db_host, db_user, db_password, db_name):
    records = []
    engine = sa.create_engine(DB_CONN.format(host=db_host, user=db_user,
                                             password=db_password, db=db_name))

    print('===== Reading solum db...')
    results = engine.execute(DB_READ_SQL)
    for row in results:
        if row['external_ref'] and 'DOCKER_IMAGE_TAG=' in row['external_ref']:
            parts = row['external_ref'].split('DOCKER_IMAGE_TAG=')
            new_ref = parts[0].strip()
            new_name = parts[1].strip()
            records.append((new_ref, new_name, row['id']))

    print('===== Updating %s rows in solum db...' % len(records))
    count = 0
    with engine.begin() as handle:
        for rec in records:
            handle.execute(text(DB_UPDATE_SQL), ref=rec[0], name=rec[1],
                           image_id=rec[2])
            count += 1
    print('===== All done, %s rows updated.' % count)


def main(args):
    db_password = getpass.getpass("Password: ")
    backup_db(args.db_host, args.db_user, db_password, args.db_name,
              args.backup_dir)
    update_db(args.db_host, args.db_user, db_password, args.db_name)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--db-host', dest='db_host', default='127.0.0.1',
                        help='default: 127.0.0.1')
    parser.add_argument('--db-user', dest='db_user', default='solum',
                        help='default: solum')
    parser.add_argument('--db-name', dest='db_name', default='solum',
                        help='default: solum')
    parser.add_argument('--backup-dir', dest='backup_dir', default='/tmp',
                        help='default: /tmp')
    args = parser.parse_args()

    main(args)
