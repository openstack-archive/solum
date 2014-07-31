#!/bin/bash

set -e

../guestagent/build-ubuntu12_04-docker.sh ../guestagent
sudo docker build -t solum/jenkins:u1204 .
sudo docker tag solum/jenkins:u1204 solum/jenkins
