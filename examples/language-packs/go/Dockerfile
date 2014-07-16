# Language pack with Go runtime
FROM ubuntu:trusty

MAINTAINER Devdatta Kulkarni <devdatta.kulkarni@rackspace.com>

RUN apt-get -yqq update && apt-get -yqq install curl build-essential libxml2-dev libxslt-dev git autoconf wget golang

ADD hello.go /tmp/hello.go

ADD testgo.sh /tmp/testgo.sh

RUN cd /tmp && bash testgo.sh

