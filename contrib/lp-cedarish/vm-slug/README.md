build heroku style buildpacks with docker + disk-image-builder
--------------------------------------------------------------

## About

This is a combination of the other two systems.  it builds a Cedarish VM via `disk-image-builder` and builds application `slugs` with docker.   `user-data` is used in conjunction with `cloud-init` to download the application slug from a web host ( should be swift, or maybe glance ) and run it.

## Requirements

### Devstack

If you want to run this in Vagrant you can use the following canned devstack

```
git clone https://github.com/rackerlabs/vagrant-solum-dev.git
cd vagrant-solum-dev
SOLUM=/path/to/code vagrant up devstack
```

If you're using your own devstack here's some useful localrc entries

```
SCREEN_LOGDIR=/opt/stack/logs/screen
ENABLED_SERVICES+=,heat,h-api,h-api-cfn,h-api-cw,h-eng
IMAGE_URLS+=,http://cc42a68525a2dda0151c-9a7653a0ba84bd9342f239dc5349667e.r38.cf1.rackcdn.com/cedarish.qcow2
```

## Using VM Builder

### Prepare Environment

This should prepare your (devstack) system to build VMs.  It will install a few system packages and the `disk-image-builder` project along with `docker` and some needed docker containers.   It also clones a bunch of git repos for the heroku buildpacks to help with auto-detection of the runtime environment needed.  Lastly it starts an apache docker container with the solum apps directory mapped to it so that VMs can download slugs.

This should be run by devstack when you include Solum,  but if it does not you can run it here.

```
/opt/stack/solum/contrib/lp-cedarish/vm-slug/prepare
```

### Cedarish VM

#### Build it

This should build the cedarish VM and upload it to glance.

```
/opt/stack/solum/contrib/lp-cedarish/vm-slug/build-cedarish
```

#### Download it

setting `IMAGE_URLS+=,http://cc42a68525a2dda0151c-9a7653a0ba84bd9342f239dc5349667e.r38.cf1.rackcdn.com/cedarish.qcow2` in `./localrc` should do this for you.  If you want to download it manually you can run the below.   You will need to upload it to glance manually once downloaded.

```
/opt/stack/solum/contrib/lp-cedarish/vm-slug/download-cedarish
```

### Build an Application

The build script takes two positional arguments.   The location of the git repo, and the app name.  The user running this script must have passwordless sudo access ( use the same user you used to install devstack ).

make sure you have an `openrc` file with your OpenStack credentials in `~/` or `~/devstack/openrc` before running this script.

The script will build a slug that will be accessible by VMs and will also create an SSH key and security groups in nova.   These can all be found in `/opt/solum/apps`   it will also provide you with the suggested `nova boot` command to start your app.


```
/opt/stack/solum/contrib/lp-cedarish/vm-slug/build-app https://github.com/paulczar/example-nodejs-express.git helloworld
```


### Deploy an Application

Your nova command to deploy your app should be something like this:

```
$ source ~/devstack/openrc
$ nova boot --flavor=2 --image=cedarish --security-groups=helloworld --key-name=helloworld_key --user-data=/opt/solum/apps/helloworld/user-data.txt helloworld01
$ nova list
+--------------------------------------+--------------+--------+------------+-------------+----------------------+
| ID                                   | Name         | Status | Task State | Power State | Networks             |
+--------------------------------------+--------------+--------+------------+-------------+----------------------+
| 92318736-5301-46ce-88e8-5dbaadeb37d6 | helloworld01 | ACTIVE | -          | Running     | private=192.168.78.2 |
+--------------------------------------+--------------+--------+------------+-------------+----------------------+
$ curl 192.168.78.2:5000
Hello World
```
