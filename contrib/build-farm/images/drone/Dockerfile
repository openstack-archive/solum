FROM ubuntu:13.04

MAINTAINER Julien Vey

RUN apt-get update
RUN apt-get install -y wget

ADD ./elements/drone/install.d/02-install-drone /tmp/install-drone.sh

RUN /tmp/install-drone.sh

EXPOSE 8080

ENTRYPOINT ["/usr/local/bin/droned"]
