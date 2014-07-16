# Language pack with Chef testing tools - FoodCritic, ChefSpec, Test Kitchen, rubocop
# The entire list is available in the accompanied Gemfile

FROM ubuntu:raring

MAINTAINER Devdatta Kulkarni <devdatta.kulkarni@rackspace.com>

RUN apt-get -yqq update && apt-get -yqq install curl build-essential libxml2-dev libxslt-dev git autoconf wget python-pip ruby1.9.3

RUN gem install bundler

ADD Gemfile /tmp/Gemfile

RUN cd /tmp && bundle install

# How to test various chef tools are installed correct?
# The languagepack author provides a test file.

ADD testgem.sh /tmp/testgem.sh

RUN cd /tmp && bash testgem.sh

