# Language pack with Chef testing tools - FoodCritic, ChefSpec, Test Kitchen, rubocop
# The entire list is available in the accompanied Gemfile

FROM ubuntu:precise

MAINTAINER Devdatta Kulkarni <devdatta.kulkarni@rackspace.com>

RUN apt-get -yqq update

RUN apt-get -yqq install build-essential libxml2-dev libxslt-dev git autoconf ruby1.9.3 libgecode-dev curl

ENV USE_SYSTEM_GECODE 1

ENV CI solum

RUN gem install bundler

ADD Gemfile /tmp/Gemfile

RUN cd /tmp && bundle install

# How to test various chef tools are installed correct?
# The languagepack author provides a test file.

ADD testgem.sh /tmp/testgem.sh

RUN cd /tmp && bash testgem.sh
