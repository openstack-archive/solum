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

In addition to Solum, your environment will also need Devstack to configure and run the requisite Openstack components, including Keystone, Glance, Nova, Neutron, and Heat.

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

Some additional configuration will be needed for Neutron, see `Neutron's Wiki page for Devstack`__

__ https://wiki.openstack.org/wiki/NeutronDevstack

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

  $ solum assembly create \
    http://10.0.2.15:9777/v1/plans/ceda0408-c93d-4772-abb2-18f65189d440 \
    --assembly=ex1
  +-------------+--------------------------------------+
  | Property    | Value                                |
  +-------------+--------------------------------------+
  | status      | None                                 |
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

  $ solum assembly show de666039-841f-45d7-9ed0-03cc3929f28e
  +-----------------+--------------------------------------+
  | Property        | Value                                |
  +-----------------+--------------------------------------+
  | status          | BUILDING                             |
  | description     | None                                 |
  | uuid            | de666039-841f-45d7-9ed0-03cc3929f28e |
  | application_uri | None                                 |
  | name            | ex1                                  |
  +-----------------+--------------------------------------+

You will see the following when the app is ready.
The :code:`status` field changes to READY and the
:code:`application_uri` is available.

::

  $ solum assembly get de666039-841f-45d7-9ed0-03cc3929f28e
  +-----------------+--------------------------------------+
  | Property        | Value                                |
  +-----------------+--------------------------------------+
  | status          | READY                                |
  | description     | None                                 |
  | uuid            | de666039-841f-45d7-9ed0-03cc3929f28e |
  | application_uri | http://192.168.76.21:5000            |
  | name            | ex1                                  |
  +-----------------+--------------------------------------+

Connect to your app
-------------------
9. Connect to your app using the value in the :code:`application_uri` field.

::

  $ curl 192.168.76.21:5000
  Hello World

Update your app
---------------
*TODO: explain git hooks*

