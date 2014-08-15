Solum Quick Start Guide
=======================

The following is a guide to deploying an app with Solum.

Overview
--------

::

  $ solum app create <plan_file>
  $ solum assembly create <assembly_name> <plan_uri> --description=<description>
  $ solum assembly get <assembly_uuid>
  $ curl <application_uri>

Vagrant Demo Environment
------------------------

We strongly recommend using this approach if you are setting up Solum for the first time.

1. Follow the `Solum Demo Instructions`__

__ https://wiki.openstack.org/wiki/Solum/Demo

Create your app
---------------

Solum clones code from the user's public Git repository. Before you begin, push your code to a public Git repo. From within your devstack host, you can now run solum commands to build and deploy your application.

2. To register an app with Solum, you will need to write a planfile to describe it.
We provide an example planfile at :code:`examples/plans/ex1.yaml`

::

  name: ex1
  description: Nodejs express.
  artifacts:
  - name: nodeus
    artifact_type: heroku
    content:
      href: https://github.com/paulczar/example-nodejs-express.git
    language_pack: auto

The app is named :code:`ex1`, and it describes a single Heroku style application, running the code from the given Github repo.
The code in that repo is a NodeJS app that listens for HTTP requests and responds with the text 'Hello World'.
We have configured this example to listen on port 5000.

Deploy your app
---------------

3. Authenticate to Keystone.
The easiest way is to use the credentials supplied by Devstack.


::

  $ source ~/devstack/openrc

4. Create an app by supplying the planfile. This registers your app with Solum.
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

5. To deploy your app, you will need to create an assembly.
Use that URI from above to create an assembly for your app.

::

  $ solum assembly create \
    ex1 \
    <your_plan_uri_here> \
    --description="test assembly"

  +-----------------+--------------------------------------------------------------------------+
  | Property        | Value                                                                    |
  +-----------------+--------------------------------------------------------------------------+
  | status          | None                                                                     |
  | description     | test assembly                                                            |
  | application_uri | None                                                                     |
  | name            | ex1                                                                      |
  | trigger_uri     | http://10.0.2.15:9777/v1/triggers/ad74f96e-7769-4462-ad90-e31b94f |
  |                 | 147c4                                                                    |
  | uuid            | de666039-841f-45d7-9ed0-03cc3929f28e                                     |
  +-----------------+--------------------------------------------------------------------------+


Solum builds a disk image by layering your app's code on top of the related language pack's image.
Once the image is created, it is uploaded to Glance.
Then, Solum creates a stack via Heat to deploy your app.
At this point, Solum is done, and in a matter of minutes your app will be deployed.

6. You can monitor the progress of your app as it builds and deploys.
The status field will show the progress of your app through the process.

::

  $ solum assembly show <your_assembly_uuid_here>
  +-----------------+--------------------------------------------------------------------------+
  | Property        | Value                                                                    |
  +-----------------+--------------------------------------------------------------------------+
  | status          | BUILDING                                                                 |
  | description     | None                                                                     |
  | application_uri | None                                                                     |
  | name            | ex1                                                                      |
  | trigger_uri     | http://10.0.2.15:9777/v1/triggers/ad74f96e-7769-4462-ad90-e31b94f |
  |                 | 147c4                                                                    |
  | uuid            | de666039-841f-45d7-9ed0-03cc3929f28e                                     |
  +-----------------+--------------------------------------------------------------------------+

7. Run the :code:`solum assembly show` command a few times to see the status change. You will notice the :code:`status` field changes to READY and the :code:`application_uri` is available.

::

  $ solum assembly show <your_assembly_uuid_here>
  +-----------------+--------------------------------------------------------------------------+
  | Property        | Value                                                                    |
  +-----------------+--------------------------------------------------------------------------+
  | status          | READY                                                                    |
  | description     | None                                                                     |
  | application_uri | 192.168.76.21:5000                                                       |
  | name            | ex1                                                                      |
  | trigger_uri     | http://10.0.2.15:9777/v1/triggers/ad74f96e-7769-4462-ad90-e31b94f |
  |                 | 147c4                                                                    |
  | uuid            | de666039-841f-45d7-9ed0-03cc3929f28e                                     |
  +-----------------+--------------------------------------------------------------------------+

Connect to Your App
-------------------
8. Connect to your app using the value in the :code:`application_uri` field.

::

  $ curl <your_application_uri_here>
  Hello World

Update Your App
---------------
You can set up your Git repository to fire an on_commit action to make a webhook call to Solum each time you make a commit. The webhook call sends a POST request to http://10.0.2.15:9777/v1/triggers/<trigger_id> causing Solum to automatically build a new image and re-deploy your application.

To do this with a GitHub repo, go to your repo on the web, click on Settings, and then select "Webhooks & Services" form the left navication menu. In the Webhooks section, click "Add Webhook", and enter your GitHub account password when prompted. Copy and paste the value of trigger_uri from your "solum assembly show" command into the "Payload URL" filed. Note that this will only work if you have a public IP address or hostname in the trigger_uri field. Select the "application/vnd.github.v3+json" Payload version, determine if you only want to trigger this webhook on "git push" or if you want it for other events too by using the radio buttons and Checkboxes provided. Finish by clicking "Add Webhook". Now next time that event is triggered on GitHub, Solum will automatically check out your change, build it, and deploy it for you.

Set up a Development Environment
--------------------------------

These instructions are for those who plan to contribute to Solum, or use features that are not yet in the latest release.

1. Clone the Solum repo.
At present it is a Stackforge project, and its repository is available on the OpenStack Git server.

::

  $ mkdir ~/Solum
  $ cd Solum
  $ git clone git://git.openstack.org/stackforge/solum

In addition to Solum, your environment will also need Devstack to configure and run the requisite Openstack components, including Keystone, Glance, Nova, Neutron, and Heat.

Vagrant Dev Environment (optional, for developers)
--------------------------------------------------

2. We have provided a Vagrant environment to deploy Solum and its required Openstack components via Devstack. We recommend using this approach if you are planning to contribute to Solum. This takes about the same amount of time as setting up Devstack manually, but it automates the setup for you.
By default, it uses virtualbox as its provisioner. We have tested this with Vagrant 1.5.4.
The environment will need to know where your Solum code is, via the environment variable :code:`SOLUM`.

::

  $ cd ~/Solum
  $ export SOLUM=~/Solum/solum
  $ git clone https://github.com/rackerlabs/vagrant-solum-dev.git vagrant
  $ cd vagrant

3. Bring up the devstack vagrant environment.
This may take a while. Allow about an hour, more or less depending on your machine speed and its connection to the internet.

::

  $ vagrant up --provision devstack
  $ vagrant ssh devstack

Devstack (alternate, for experts)
---------------------------------

Using Vagrant is not a requirement for deploying Solum.
You may instead opt to install Solum and Devstack yourself. Keep in mind that this approach is much slower than using the Vagrant option. It may take an hour or more to complete this setup step. Please set your expectations accordingly.
The details of integrating Solum with Devstack can be found in :code:`contrib/devstack/README.rst`.
