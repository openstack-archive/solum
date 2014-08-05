#!/bin/bash

set -e

DOCKERFILE_PATH="."
if [[ ! -z "$1" ]]; then
    DOCKERFILE_PATH=$1
fi

sudo docker build -t solum/guestagent:u1304 $DOCKERFILE_PATH
sudo docker tag solum/guestagent:u1304 solum/guestagent
