#!/bin/bash

DIB_RELEASE="raring"
ELEMENTS_PATH=./elements disk-image-create --no-tmpfs -a amd64 vm ubuntu gitolite -o u1304-gitolite.qcow2
