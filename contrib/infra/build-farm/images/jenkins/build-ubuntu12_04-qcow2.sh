#!/bin/bash

export DIB_RELEASE=precise
ELEMENTS_PATH=../../../diskimage-builder/elements disk-image-create --no-tmpfs -a amd64 vm ubuntu guestagent jenkins -o u1204-build-jenkins.qcow2
