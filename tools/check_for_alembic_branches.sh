#!/bin/sh
HEADS=$(alembic -c solum/objects/sqlalchemy/migration/alembic.ini branches | grep head | wc -l)
if [ $HEADS -gt 1 ]; then
    echo "ERROR: there are multiple alembic migration branches"
    alembic -c solum/objects/sqlalchemy/migration/alembic.ini branches
    exit 1
fi
exit 0
