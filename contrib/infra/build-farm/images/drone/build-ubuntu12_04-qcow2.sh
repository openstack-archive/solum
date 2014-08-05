#!/bin/bash

export DIB_RELEASE=precise
ELEMENTS_PATH=./elements disk-image-create --no-tmpfs -a amd64 vm ubuntu drone -o u1204-build-drone.qcow2
