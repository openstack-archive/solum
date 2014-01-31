Git Push POC
============

## About

git push workflow example which combines with `contrib/lp-cedarish/vm-slug`

These scripts represent a workflow that solum could use internally to create and deploy applications.   the `create-app` and `deploy-app` scripts would be solum CLI commands, the rest would be internal solum magic and are just represented as scripts for POC purposes.

These scripts should never be part of a production install of Solum and will likely be removed as their workflows are integrated into solum itself,  or discarded if alternative workflows are used.

These scripts may rely on external tools and applications stored on github which may change wihtout notice.  You should vet these before running and should also probably fork them and repoint the scripts at your forks.

See `contrib/lp-cedarish/vm-slug/README.md` for more details on the build environment.

## Requirements

### Devstack

If you want to run this in Vagrant you can use the following canned devstack

```
$ git clone https://github.com/rackerlabs/vagrant-solum-dev.git
$ cd vagrant-solum-dev
$ SOLUM=/path/to/code vagrant up devstack
```

## Using

### Install

run this as the same user you installed devstack with to get a free ride on the passwordless sudo bus.  This will set up your git server, download a pre-baked cedarish VM, set up the build tooling, and push the cedarish VM to glance.

```
$ /solum/contrib/example-gitpush/prepare
```

### Create Application

This will add a repo to the solum git server and add it as a remote repo of your local git repo.

```
$ cd /tmp
$ git clone https://github.com/paulczar/example-nodejs-express.git nodejs
$ cd nodejs
$ /solum/contrib/example-gitpush/create-app
[master 9a0f18d] adding repo and key for nodejs
 Committer: vagrant <vagrant@devstack>
 1 file changed, 4 insertions(+)
Counting objects: 7, done.
Delta compression using up to 2 threads.
Compressing objects: 100% (3/3), done.
Writing objects: 100% (4/4), 366 bytes, done.
Total 4 (delta 1), reused 0 (delta 0)
remote: Initialized empty Git repository in /opt/git/repositories/nodejs.git/
To git@127.0.0.1:gitolite-admin
   75db5b8..9a0f18d  master -> master
```

### Push your data to the App

```
$ git push solum master
 1 file changed, 1 insertion(+)
Counting objects: 5, done.
Delta compression using up to 2 threads.
Compressing objects: 100% (3/3), done.
Writing objects: 100% (3/3), 271 bytes, done.
Total 3 (delta 2), reused 0 (delta 0)
remote: SHA of head e046e00eb09b72bee130430159127a342c01cc94
-----> Node.js app detected
-----> Requested node range: 0.10.x
-----> Resolved node version: 0.10.25
-----> Downloading and installing node
-----> Restoring node_modules directory from cache
-----> Pruning cached dependencies not specified in package.json
       npm WARN package.json example-nodejs-express@0.0.1 No repository field.
-----> Installing dependencies
       npm WARN package.json example-nodejs-express@0.0.1 No repository field.
-----> Caching node_modules directory for future builds
-----> Cleaning up node-gyp and npm artifacts
-----> Building runtime environment
-----> Discovering process types
       Procfile declares types -> web
-----> Compiled slug size is 5.6M
remote: 62441108436bfed9e21cf44db167022fe60c65caa99fb4ca82d45f9de64ce0b9
remote: APP BUILT!!
To git@127.0.0.1:nodejs
   a2e48d4..e046e00  master -> master
```

### Deploy your app

This will create a security group, an ssh key in `/opt/solum/apps/<sha>/key.priv`, and launch a vm.    The VM uses user-data stored in `/opt/solum/apps/sha/user-data.txt` to download, install, and run the application slug built during the git push.

```
$ /solum/contrib/example-gitpush/deploy-app
+----+--------+----------------------------------+
| Id | Name   | Description                      |
+----+--------+----------------------------------+
| 4  | nodejs | allow ssh/web to nodejs instance |
+----+--------+----------------------------------+
+-------------+-----------+---------+-----------+--------------+
| IP Protocol | From Port | To Port | IP Range  | Source Group |
+-------------+-----------+---------+-----------+--------------+
| tcp         | 22        | 22      | 0.0.0.0/0 |              |
+-------------+-----------+---------+-----------+--------------+
+-------------+-----------+---------+-----------+--------------+
| IP Protocol | From Port | To Port | IP Range  | Source Group |
+-------------+-----------+---------+-----------+--------------+
| tcp         | 5000      | 5000    | 0.0.0.0/0 |              |
+-------------+-----------+---------+-----------+--------------+
+--------------------------------------+-------------------------------------------------+
| Property                             | Value                                           |
+--------------------------------------+-------------------------------------------------+
| OS-DCF:diskConfig                    | MANUAL                                          |
| OS-EXT-AZ:availability_zone          | nova                                            |
| OS-EXT-STS:power_state               | 0                                               |
| OS-EXT-STS:task_state                | scheduling                                      |
| OS-EXT-STS:vm_state                  | building                                        |
| OS-SRV-USG:launched_at               | -                                               |
| OS-SRV-USG:terminated_at             | -                                               |
| accessIPv4                           |                                                 |
| accessIPv6                           |                                                 |
| adminPass                            | 5ovU9E2pnMZR                                    |
| config_drive                         |                                                 |
| created                              | 2014-01-31T19:42:39Z                            |
| flavor                               | m1.small (2)                                    |
| hostId                               |                                                 |
| id                                   | 9b50c765-e811-44a7-bf0f-a5d52ad6dbb4            |
| image                                | cedarish (9654b39e-a340-4ddf-822b-ad67f9aa5f5c) |
| key_name                             | -                                               |
| metadata                             | {}                                              |
| name                                 | nodejs01                                        |
| os-extended-volumes:volumes_attached | []                                              |
| progress                             | 0                                               |
| security_groups                      | nodejs                                          |
| status                               | BUILD                                           |
| tenant_id                            | 06a788275a6f458cb1ad6ab061face7f                |
| updated                              | 2014-01-31T19:42:39Z                            |
| user_id                              | 693cbc7b4cf04c8a9e4cabfb49a37d62                |
+--------------------------------------+-------------------------------------------------+
```

if you're running this in devstack on a vm on your laptop like I do,  this step can take some time.  I usually kick off a `watch` job so I can see what is happening:

```
$ source ~/devstack/openrc
$ nova list
+--------------------------------------+----------+--------+------------+-------------+-----------------------+
| ID                                   | Name     | Status | Task State | Power State | Networks              |
+--------------------------------------+----------+--------+------------+-------------+-----------------------+
| 1b380721-2030-4797-b829-bb4bb38cd633 | nodejs01 | ACTIVE | -          | Running     | private=192.168.78.21 |
+--------------------------------------+----------+--------+------------+-------------+-----------------------+
$ watch 'nova console-log --length=5 1b380721-2030-4797-b829-bb4bb38cd633'
```

when the output looks like this it means it's done:

```
Every 2.0s: nova console-log --length=5 40f95d1b-eee3-4de6-8549-15eaff2cca95                                                                                           Fri Jan 31 21:13:40 2014

ecdsa-sha2-nistp256 AAAAE2VjZHNhLXNoYTItbmlzdHAyNTYAAAAIbmlzdHAyNTYAAABBBEt/agOdXF6PCQYOeC3JjCETxNx963vS7N64kWePccQ/g6iDoGWO1TrCahEo2H88RtVtqcGqr8NJggGf3FyLuWY= root@nodejs01
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDtG6nLUPZf4GC3+bc8SLOLZq4Jzm/untvTYfr0+0mAitnVT7O9ckUtLrIi4YiQLAmKJB5FCczOtEF4gek2gdW3kgMmTmMmfWBfXOsWMRDltGAy0zoQu6pcjWiXUg88H/5BMfQF2QExDf02Dt26yhBSOPf
MIdFc+VT+Qs77E/kp3ErP5y3oH6b3prpQSaBOucMnLkFp9nIpM3Jukcycuj2GMY4XlSuw0gvxPZNkZSNUvuNWClipxnPyKy8i/47YUR+JblRFN7CpdmwUGltNnx8YWHO9maH57uDrIusJ5c4sxUa1ZlNLxEWmT03QVSIhgtTbLcbCWz3VKpadnZXC9O// r
oot@nodejs01
-----END SSH HOST KEY KEYS-----
Cloud-init v. 0.7.3 finished at Fri, 31 Jan 2014 21:12:11 +0000. Datasource DataSourceConfigDriveNet [net,ver=2][source=/dev/sr0].  Up 285.18 seconds
```

and you should be able to hit the app:

```
$ curl 192.168.78.21:5000
Hello World
```

A lot of effort to go to for a hello world...
