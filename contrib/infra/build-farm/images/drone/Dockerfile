FROM solum/guestagent

MAINTAINER Julien Vey

RUN apt-get update
RUN apt-get install -y wget

ADD ../../../diskimage-builder/elements/drone/install.d/02-install-drone /tmp/install-drone.sh

RUN /tmp/install-drone.sh

EXPOSE 8080

ENTRYPOINT ["/usr/local/bin/droned"]
