FROM ubuntu:13.04

MAINTAINER Julien Vey

RUN apt-get update
RUN apt-get install -y wget

ADD ./elements/drone/install.d/02-install-drone /tmp/install-drone.sh

RUN /tmp/install-drone.sh
