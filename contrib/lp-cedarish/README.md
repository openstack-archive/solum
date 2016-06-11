Cedarish Language Pack Examples
-------------------------------

What even is?
=============

Cedarish is a stack developed for Docker style PAAS to deploy Heroku buildpacks.  The original project can be found [here](https://github.com/progrium/cedarish).

This is an example implementation of a Cedarish Language Pack for Solum. 

This has been implemented ( as a POC/MVP ) to build/run Heroku buildpacks upon both regular VMs and the Docker driver on top of devstack.

Read the README files in the `docker`, `vm` dirs for details on building/running apps in various scenarios.

It was built and tested on top of the rackerlabs [solum dev environment](https://github.com/rackerlabs/vagrant-solum-dev).

Usage
=====

Follow the `readme` in either `docker`, or `vm` to install the appropriate tooling.

Example Apps
------------

Examples forked for stability from the [Opdemand](https://github.com/opdemand) project at github.

Python - https://github.com/paulczar/example-python-django
Java   - https://github.com/paulczar/example-java-jetty
NodeJS - https://github.com/paulczar/example-nodejs-express.git
