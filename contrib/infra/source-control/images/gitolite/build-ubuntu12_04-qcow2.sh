#!/bin/bash

export DIB_RELEASE=precise
ELEMENTS_PATH=./elements disk-image-create --no-tmpfs -a amd64 vm ubuntu gitolite -o u1204-gitolite.qcow2
