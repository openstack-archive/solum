#!/bin/sh
args=
if [ -n "$@" ] ; then
    args="-t $@"
fi
python setup.py testr --coverage --slowest "$args"
python -m coverage report --show-missing
echo "Coverage generated, see cover/index.html"
