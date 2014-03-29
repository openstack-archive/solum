# docker builder!

build heroku style buildpacks with docker

# Requirements

## Devstack + Docker Driver

If you want to run this in Vagrant you can use the following canned devstack:

```
git clone https://github.com/rackerlabs/vagrant-solum-dev.git
cd vagrant-solum-dev
DOCKER=true SOLUM=/path/to/code vagrant up devstack
```

# Using Docker Builder

## Prepare Environment

This should prepare your system to use the docker builder by building a few containers and syncing down the heroku buildpacks.  Currently requires sudo access to work with docker.   Run it as the same user you installed devstack which has passwordless sudo.

```
/opt/stack/solum/contrib/lp-cedarish/docker/prepare
```

## Build an Application

The build script takes two positional arguments.   The location of the git repo, and the app name.  Currently requires sudo access to work with docker.   Run it as the same user you installed devstack which has passwordless sudo.

```
$ source ~/devstack/openrc
$ keystone tenant-get $OS_TENANT_NAME
# get the tenant_id and pass that into build-app

/opt/stack/solum/contrib/lp-cedarish/docker/build-app https://github.com/paulczar/example-nodejs-express.git nodejs $OS_TENANT_ID
```

This script will upload a docker container with your built application to glance to be run via nova.

## Deploy an Application

Due to a bug with the docker driver the first VM you start will run `sh` instead of the embedded `CMD`.  thus we should kick off a dummy build first

```
$ nova image-list
+--------------------------------------+---------------------------------+--------+--------+
| ID                                   | Name                            | Status | Server |
+--------------------------------------+---------------------------------+--------+--------+
| 0df6ccbc-c43c-4e4d-9caa-3ddf5485b51b | docker-busybox:latest           | ACTIVE |        |
| 8d558f99-02a9-4b9e-98ac-9bb65009ecda | nodejs:latest                   | ACTIVE |        |
+--------------------------------------+---------------------------------+--------+--------+
$ nova boot --flavor 1 --image docker-busybox:latest dummy
$ nova delete dummy
$ nova boot --flavor 1 --image nodejs:latest nodejs01
$ nova boot --flavor 1 --image nodejs:latest nodejs02
$ nova list
+--------------------------------------+----------+--------+------------+-------------+-----------------------+
| ID                                   | Name     | Status | Task State | Power State | Networks              |
+--------------------------------------+----------+--------+------------+-------------+-----------------------+
| b4ac0b33-42da-4efa-8580-28b1627199b8 | nodejs01 | ACTIVE | -          | Running     | private=192.168.78.21 |
| 1697f9fa-9c2c-44b3-b13b-87f7bd3a96c6 | nodejs02 | ACTIVE | -          | Running     | private=192.168.78.22 |
+--------------------------------------+----------+--------+------------+-------------+-----------------------+
$ curl http://192.168.78.21:5000
Hello World
$ curl http://192.168.78.22:5000
Hello World
```
