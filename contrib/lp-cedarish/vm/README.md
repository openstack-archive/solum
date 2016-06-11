build heroku style buildpacks with disk-image-builder
-----------------------------------------------------

## Requirements

### Devstack

If you want to run this in Vagrant you can use the following canned devstack

```
git clone https://github.com/rackerlabs/vagrant-solum-dev.git
cd vagrant-solum-dev
SOLUM=/path/to/code vagrant up devstack
```

## Using VM Builder

### Prepare Environment

This should prepare your (devstack) system to build VMs.  It will install a few system packages and the `disk-image-builder` project.   Run this as the same user you installed devstack as to get passwordless sudo access.

```
/opt/stack/solum/contrib/lp-cedarish/vm/prepare
```

### Build an Application

The build script takes two positional arguments.   The location of the git repo, and the app name.  The user running this script must have passwordless sudo access ( use the same user you used to install devstack ).

make sure you have an `openrc` file with your OpenStack credentials in `~/` or `~/devstack/openrc` before running this script.

```
/opt/stack/solum/contrib/lp-cedarish/vm/build-app https://github.com/paulczar/example-nodejs-express.git helloworld
```

The script should update glance with the resultant image as well as set up a sshkey and security-group.  it will provide you with the nova command required to boot the instance as well as a basic `user-data.txt` to set any environment variables ( to be passed to your app ) and run the app on boot. 

### Deploy an Application

Your nova command to deploy your app should be something like this:


```
$ source ~/devstack/openrc
$ nova boot --flavor=2 --image=helloworld --security-groups=helloworld --key-name=helloworld_key --user-data=/opt/stack/solum/contrib/lp-cedarish/vm/user-data.txt helloworld01
$ nova list
+--------------------------------------+--------------+--------+------------+-------------+----------------------+
| ID                                   | Name         | Status | Task State | Power State | Networks             |
+--------------------------------------+--------------+--------+------------+-------------+----------------------+
| 92318736-5301-46ce-88e8-5dbaadeb37d6 | helloworld01 | ACTIVE | -          | Running     | private=192.168.78.2 |
+--------------------------------------+--------------+--------+------------+-------------+----------------------+
$ curl 192.168.78.2:5000
Hello World
```
