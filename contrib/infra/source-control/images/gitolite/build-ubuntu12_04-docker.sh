#!/bin/bash

[[ -f admin.pub ]] || ssh-keygen -t rsa -N "" -f admin
sudo docker build -t u1204-gitolite .
