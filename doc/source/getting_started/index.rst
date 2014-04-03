Solum Quick Start Guide
=======================

The following is a guide to deploying an app with Solum.

Overview
--------

::

  $ solum app create <plan file>
  $ solum assembly create <plan uri> --assembly=<app name>
  $ solum assembly get <assembly uuid>
  $ curl <app ip>

Set up your environment
-----------------------

1. You will need to clone Solum.
At present it is a Stackforge project, and its repository is available on Github.

::

  $ mkdir ~/Solum
  $ cd Solum
  $ git clone https://github.com/stackforge/solum

In addition to Solum, your environment will also need Devstack to configure and run the requisite Openstack components, including Keystone, Glance, Nova, and Heat.

Vagrant (Optional)
------------------

2. We have provided a vagrant environment to deploy Solum and its required Openstack components via Devstack.
By default, it uses virtualbox as its provisioner.
The environment will need to know where your Solum code is, via the environment variable :code:`SOLUM`.

::

  $ cd ~/Solum
  $ export SOLUM=~/Solum/solum
  $ git clone https://github.com/rackerlabs/vagrant-solum-dev.git vagrant
  $ cd vagrant

3. Bring up the devstack vagrant environment.
This may take a while.

::

  $ vagrant up --provision devstack
  $ vagrant ssh devstack

Devstack (alternate)
--------------------

Using Vagrant is not a requirement for deploying Solum.
You may instead opt to install Solum and Devstack yourself.
The details of integrating Solum with Devstack can be found in :code:`contrib/devstack/README.rst`.

Create your app
---------------

Solum clones your code from its repository on github.com, so naturally you will first need to push your code to a public repository.

4. To register an app with Solum, you will need to write a planfile to describe it.
We provide an example planfile at :code:`examples/plans/ex1.yaml`

::

  name: ex1
  description: Nodejs express.
  artifacts:
  - name: nodeus
    artifact_type: application.heroku
    content:
      href: https://github.com/paulczar/example-nodejs-express.git
    language_pack: auto

The app is named :code:`ex1`, and it describes a single Heroku style application, running the code from the given Github repo.
The code in that repo is a NodeJS app that listens for HTTP requests and responds with the text 'Hello World'.
We have configured this example to listen on port 5000.

Deploy your app
---------------

5. Authenticate to Keystone.
The easiest way is to use the credentials supplied by Devstack.


::

  $ source ~/devstack/openrc

6. Create an app by supplying the planfile. This registers your app with Solum.
For demonstration purposes, we will use the provided example.

::

  $ solum app create /opt/stack/solum/examples/plans/ex1.yaml
  +-------------+---------------------------------------------------------------------+
  | Property    | Value                                                               |
  +-------------+---------------------------------------------------------------------+
  | description | Nodejs express.                                                     |
  | uri         | http://10.0.2.15:9777/v1/plans/ceda0408-c93d-4772-abb2-18f65189d440 |
  | uuid        | ceda0408-c93d-4772-abb2-18f65189d440                                |
  | name        | ex1                                                                 |
  +-------------+---------------------------------------------------------------------+

The :code:`uri` field above refers to the newly-registered plan.
At this point, your app is not deployed yet.

7. To deploy your app, you will need to create an assembly.
Use that URI from above to create an assembly for your app.

::

  $ solum assembly create http://10.0.2.15:9777/v1/plans/ceda0408-c93d-4772-abb2-18f65189d440 --assembly=ex1
  +-------------+--------------------------------------+
  | Property    | Value                                |
  +-------------+--------------------------------------+
  | status      |                                      |
  | description | None                                 |
  | uuid        | de666039-841f-45d7-9ed0-03cc3929f28e |
  | name        | ex1                                  |
  +-------------+--------------------------------------+

Solum builds a disk image by layering your app's code on top of the related language pack's image.
Once the image is created, it is uploaded to Glance.
Then, Solum creates a stack via Heat to deploy your app.
At this point, Solum is done, and in a matter of minutes your app will be deployed.

8. You can monitor the progress of your app as it builds and deploys.
The status field will show the progress of your app through the process.

::

  $ solum assembly get de666039-841f-45d7-9ed0-03cc3929f28e
  +-------------+--------------------------------------+
  | Property    | Value                                |
  +-------------+--------------------------------------+
  | status      |                                      |
  | description | None                                 |
  | uuid        | de666039-841f-45d7-9ed0-03cc3929f28e |
  | name        | ex1                                  |
  +-------------+--------------------------------------+

You can also check on your app in Heat.

::

  $ heat stack-show ex1
  +----------------------+-----------------------------------------------------------------------------------------------------------+
  | Property             | Value                                                                                                     |
  +----------------------+-----------------------------------------------------------------------------------------------------------+
  | capabilities         | []                                                                                                        |
  | creation_time        | 2014-04-01T18:09:32Z                                                                                      |
  | description          | Basic app deploy.                                                                                         |
  | disable_rollback     | True                                                                                                      |
  | id                   | 309ecf99-7e05-48c2-8264-66b55fde2dc2                                                                      |
  | links                | http://10.0.2.15:8004/v1/313094c3e4044500aab2c7956b8a0716/stacks/ex1/309ecf99-7e05-48c2-8264-66b55fde2dc2 |
  | notification_topics  | []                                                                                                        |
  | outputs              | [                                                                                                         |
  |                      |   {                                                                                                       |
  |                      |     "output_value": "192.168.78.21",                                                                      |
  |                      |     "description": "The public IP address of the newly configured Server.",                               |
  |                      |     "output_key": "public_ip"                                                                             |
  |                      |   },                                                                                                      |
  |                      |   {                                                                                                       |
  |                      |     "output_value": "http://192.168.78.21:5000",                                                          |
  |                      |     "description": "The URL for the Server.",                                                             |
  |                      |     "output_key": "URL"                                                                                   |
  |                      |   }                                                                                                       |
  |                      | ]                                                                                                         |
  | parameters           | {                                                                                                         |
  |                      |   "OS::stack_id": "309ecf99-7e05-48c2-8264-66b55fde2dc2",                                                 |
  |                      |   "OS::stack_name": "ex1",                                                                                |
  |                      |   "key_name": "",                                                                                         |
  |                      |   "image": "590cdd36-efb3-4c11-885e-b92aacfc88df",                                                        |
  |                      |   "flavor": "m1.small",                                                                                   |
  |                      |   "port": "5000",                                                                                         |
  |                      |   "app_name": "ex1"                                                                                       |
  |                      | }                                                                                                         |
  | stack_name           | ex1                                                                                                       |
  | stack_status         | CREATE_COMPLETE                                                                                           |
  | stack_status_reason  | Stack CREATE completed successfully                                                                       |
  | template_description | Basic app deploy.                                                                                         |
  | timeout_mins         | 60                                                                                                        |
  | updated_time         | None                                                                                                      |
  +----------------------+-----------------------------------------------------------------------------------------------------------+

Connect to your app
-------------------
9. In the output of :code:`heat stack-show ex1`, you will see :code:`public_ip` mentioned in the details of :code:`outputs`.
That is the public IP your app is listening on.

::

  $ heat stack-show ex1 | grep -B 2 public_ip
  |                      |     "output_value": "192.168.78.21",                                                                      |
  |                      |     "description": "The public IP address of the newly configured Server.",                               |
  |                      |     "output_key": "public_ip"

10. Connect to your app via that IP.
The example app deployed in this text listens on port 5000 by default.

::

  $ curl 192.168.76.21:5000
  Hello World

Update your app
---------------
*TODO: explain git hooks*

*TODO: Remove Heat mentions in 8 and 9 after url and status are in assembly*
