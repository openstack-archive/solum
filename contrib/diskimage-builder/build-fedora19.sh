#!/bin/bash

ELEMENTS_PATH=./elements disk-image-create --no-tmpfs -a amd64 vm fedora tomcat -o f19-tomcat7-openjdk1.7.qcow2
