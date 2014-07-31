#!/bin/bash

set -e

../guestagent/build-ubuntu12_04-docker.sh ../guestagent
sudo docker build -t solum/drone:u1204 .
sudo docker tag solum/drone:u1204 solum/drone
