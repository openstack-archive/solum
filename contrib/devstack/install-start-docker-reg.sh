#!/bin/bash

# Installs and runs docker registry on port 5042
# Tested on: Ubuntu 14.04

# Storage: local (in /tmp) of the host
# Docker images are stored in /tmp/registry/images
# Docker repositories are stored in /tmp/registry/repositories

# How to test?
# 1) Create a docker image
# 2) Tag it (e.g. docker tag <IP>:5042/test-image)
# 3) Push the image (docker push <IP>:5042/test-image)
# 4) Pull the image from a different host (docker pull <IP>:5042/test-image)

# <IP>: IP address of the host running the docker registry


# install dependencies
sudo apt-get update
sudo apt-get -y install build-essential python-dev libevent-dev python-pip liblzma-dev git libssl-dev python-m2crypto swig

# clone docker registry
sudo git clone https://github.com/dotcloud/docker-registry.git /opt/docker-registry
pushd /opt/docker-registry
pip install -r requirements/main.txt
popd

# install docker
curl -sSL https://get.docker.com/ubuntu/ | sudo sh

# install docker registry
pip_command=`which pip`
pip_build_tmp=$(mktemp --tmpdir -d pip-build.XXXXX)
$pip_command install /opt/docker-registry --build=${pip_build_tmp}

# initialize config file
cp /opt/docker-registry/docker_registry/lib/../../config/config_sample.yml /opt/docker-registry/docker_registry/lib/../../config/config.yml

# start docker registry
gunicorn --access-logfile - --debug -k gevent -b 0.0.0.0:5042 -w 1 docker_registry.wsgi:application &

# clean-up
rm -rf ${pip_build_tmp}
