#!/bin/bash

export DIB_RELEASE=precise
ELEMENTS_PATH=../../../diskimage-builder/elements disk-image-create --no-tmpfs -a amd64 vm ubuntu guestagent drone -o u1204-build-drone.qcow2
