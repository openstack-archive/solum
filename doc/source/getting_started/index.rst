Solum Quick Start Guide
=======================

The following is a guide to deploying an app with Solum.

Overview
--------

::

  $ solum languagepack create <NAME> <GIT_REPO>
  $ solum languagepack show <UUID\Name>
  $ solum languagepack logs <UUID>
  $ solum languagepack list
  $ solum app create --plan-file <plan_file> [--param-file param_file]
  $ solum assembly show <assembly_uuid>
  $ curl <application_uri>

Vagrant Demo Environment
------------------------

We strongly recommend using this approach if you are setting up Solum for the first time.

1. Follow the `Solum Demo Instructions`__

__ https://wiki.openstack.org/wiki/Solum/Demo

In this document we will work with a python example to demonstrate how you can use solum to deploy an application.

Create a languagepack
---------------------

Before deploying an app on Solum, we need to create a run time environment, called languagepack, for the application.
To learn more, see the languagepacks section of this document.

::

  $ solum languagepack create python https://github.com/rackspace-solum-samples/solum-languagepack-python.git
  +-------------+--------------------------------------+
  | Property    | Value                                |
  +-------------+--------------------------------------+
  | status      | PENDING                              |
  | description | None                                 |
  | uuid        | 96f889e7-e8db-4ae3-a38d-0bfda8268e30 |
  | name        | python                               |
  +-------------+--------------------------------------+

Solum takes a few minutes to build your languagepack. You can check the state by using the languagepack show command.
A languagepack is ready for use once the state changes to 'READY'.

::

  $ solum languagepack show 96f889e7-e8db-4ae3-a38d-0bfda8268e30
  +-------------+--------------------------------------------------------------------------+
  | Property    | Value                                                                    |
  +-------------+--------------------------------------------------------------------------+
  | status      | READY                                                                    |
  | source_uri  | https://github.com/rackspace-solum-samples/solum-languagepack-python.git |
  | description | None                                                                     |
  | uuid        | 96f889e7-e8db-4ae3-a38d-0bfda8268e30                                     |
  | name        | python                                                                   |
  +-------------+--------------------------------------------------------------------------+

You can check logs that were generated while building the languagepack with the following command.
This is a great way to debug your languagepack if it fails to build.

::

  $ solum languagepack logs 96f889e7-e8db-4ae3-a38d-0bfda8268e30
  +--------------------------------------+-----------------------------------------------------------------------------+
  | resource_uuid                        | local_storage                                                               |
  +--------------------------------------+-----------------------------------------------------------------------------+
  | 96f889e7-e8db-4ae3-a38d-0bfda8268e30 | /var/log/solum/worker/languagepack-840d51c0-7a4d-4a3c-a2af-452de076eed8.log |
  +--------------------------------------+-----------------------------------------------------------------------------+

You can find all available languagepacks with the following command

::

  $ solum languagepack list
  +--------------------------------------+--------+-------------+--------+--------------------------------------------------------------------------+
  | uuid                                 | name   | description | status | source_uri                                                               |
  +--------------------------------------+--------+-------------+--------+--------------------------------------------------------------------------+
  | 95310b74-b3ed-4150-b0bf-e64c21359900 | java   | None        | READY  | https://github.com/rackspace-solum-samples/solum-languagepack-java.git   |
  | 96f889e7-e8db-4ae3-a38d-0bfda8268e30 | python | None        | READY  | https://github.com/rackspace-solum-samples/solum-languagepack-python.git |
  +--------------------------------------+--------+-------------+--------+--------------------------------------------------------------------------+


Create your app
---------------

Solum clones code from the user's public Git repository or user's public/private GitHub repository. Before you begin, push your code to a Git repo. From within your devstack host, you can now run solum commands to build and deploy your application.

2. To register an app with Solum, you will need to write a planfile to describe it.
The following plan file deploys a sample python application.
You can find other examples in the :code:`examples/plans/` folder of the solum repo on github.
To learn more, see the planfile section of this document.

::

  version: 1
  name: python-sample-app
  description: Sample Python web app.
  artifacts:
  - name: python-sample-app
    content:
      href: https://github.com/rackspace-solum-samples/solum-python-sample-app.git
    language_pack: python
    unittest_cmd: pip install -r test-requirements.txt; pep8 app.py
    run_cmd: ./main.sh
    ports: 80

The app is named :code:`python-sample-app`, and it describes a single application, running the code from the given Github repo.
The code in that repo is a Python app that listens for HTTP requests and returns environment variables supplied by the user during app creation.
We have configured this example to listen on port 80.

Deploy your app
---------------

3. Authenticate to Keystone.
The easiest way is to use the credentials supplied by Devstack.


::

  $ source ~/devstack/openrc

4. Create an app by supplying the planfile. This registers your app with Solum.
For demonstration purposes, we will use the provided example.

::

  $ solum app create --plan-file planfile.yaml --param-file params.yaml
  +-------------+---------------------------------------------------------------------+
  | Property    | Value                                                               |
  +-------------+---------------------------------------------------------------------+
  | description | Sample Python web app.                                              |
  | uri         | http://10.0.2.15:9777/v1/plans/4a795b99-936d-4330-be4d-d2099b160075 |
  | name        | python-sample-app                                                   |
  | trigger_uri |                                                                     |
  | uuid        | 4a795b99-936d-4330-be4d-d2099b160075                                |
  +-------------+---------------------------------------------------------------------+

The :code:`uri` field above refers to the newly-registered plan.
At this point, your app is not deployed yet.

5. Your app is now ready to be deployed using the uuid from above to deploy your app.

::

  $ solum app deploy 4a795b99-936d-4330-be4d-d2099b160075
  +-----------------+------------------------------------------------------------------------+
  | Property        | Value                                                                  |
  +-----------------+------------------------------------------------------------------------+
  | status          | QUEUED                                                                 |
  | description     | Sample Python web app.                                                 |
  | application_uri | None                                                                   |
  | name            | python-sample-app                                                      |
  | trigger_uri     | http://10.0.2.15:9777/v1/triggers/b6eb26e5-3b7b-416b-b932-302c514071cc |
  | uuid            | 185f2741-61e0-497e-b2b7-c890c7e151dd                                   |
  +-----------------+------------------------------------------------------------------------+


Solum builds a docker image by layering your app's code on top of the related language pack's image.
Then, Solum creates a stack via Heat to deploy your app.
At this point, Solum is done, and in a matter of minutes your app will be deployed.

6. You can monitor the progress of your app as it builds and deploys.
The status field will show the progress of your app through the process.

::

  $ solum assembly show 185f2741-61e0-497e-b2b7-c890c7e151dd
  +-----------------+------------------------------------------------------------------------+
  | Property        | Value                                                                  |
  +-----------------+------------------------------------------------------------------------+
  | status          | BUILDING                                                               |
  | description     | Sample Python web app.                                                 |
  | application_uri | None                                                                   |
  | created_at      | 2015-03-10T22:47:04                                                    |
  | updated_at      | 2015-03-10T22:49:59                                                    |
  | name            | python-sample-app                                                      |
  | trigger_uri     | http://10.0.2.15:9777/v1/triggers/b6eb26e5-3b7b-416b-b932-302c514071cc |
  | uuid            | 185f2741-61e0-497e-b2b7-c890c7e151dd                                   |
  +-----------------+------------------------------------------------------------------------+

7. Run the :code:`solum assembly show` command a few times to see the status change. You will notice the :code:`status` field changes to READY and the :code:`application_uri` is available.

::

  $ solum assembly show 185f2741-61e0-497e-b2b7-c890c7e151dd
  +-----------------+------------------------------------------------------------------------+
  | Property        | Value                                                                  |
  +-----------------+------------------------------------------------------------------------+
  | status          | READY                                                                  |
  | description     | Sample Python web app.                                                 |
  | application_uri | 192.168.76.21:80                                                       |
  | created_at      | 2015-03-10T22:47:04                                                    |
  | updated_at      | 2015-03-10T22:49:59                                                    |
  | name            | python-sample-app                                                      |
  | trigger_uri     | http://10.0.2.15:9777/v1/triggers/b6eb26e5-3b7b-416b-b932-302c514071cc |
  | uuid            | 185f2741-61e0-497e-b2b7-c890c7e151dd                                   |
  +-----------------+------------------------------------------------------------------------+

Connect to Your App
-------------------
8. Connect to your app using the value in the :code:`application_uri` field.

::

  $ curl <your_application_uri_here>
  Hello World

Update Your App
---------------
You can set up your Git repository to fire an on_commit action to make a webhook call to Solum each time you make a commit. The webhook call sends a POST request to http://10.0.2.15:9777/v1/triggers/<trigger_id> causing Solum to automatically build a new image and re-deploy your application.

To do this with a GitHub repo, go to your repo on the web, click on Settings, and then select "Webhooks & Services" form the left navigation menu. In the Webhooks section, click "Add Webhook", and enter your GitHub account password when prompted. Copy and paste the value of trigger_uri from your "solum assembly show" command into the "Payload URL" filed. Note that this will only work if you have a public IP address or hostname in the trigger_uri field. Select the "application/vnd.github.v3+json" Payload version, determine if you only want to trigger this webhook on "git push" or if you want it for other events too by using the radio buttons and Checkboxes provided. Finish by clicking "Add Webhook". Now next time that event is triggered on GitHub, Solum will automatically check out your change, build it, and deploy it for you.

Languagepacks
-------------
Languagepacks define the runtime environment required by your application.

To build a languagepack, solum requires a git repo containing a Dockerfile. Solum creates a Docker and stores the image for use when building and deploying your application.
See the sample languagepack repo below

::

  $ https://github.com/rackspace-solum-samples/solum-languagepack-python

Here are some best practices to keep in mind while creating a languagepack

1. A good languagepack is reusable across application
2. All Operating system level libraries should be defined in the languagepack
3. Test tools should be installed in the languagepack
4. Includes a mandatory build.sh script, which Solum CI expects and executes during the build phase

planfile
--------

A planfile is used to define your application and passed in during application creation.

::

  $ solum app create --plan-file planfile.yaml --param-file params.yaml

In the above command, we use the --plan-file flag to provide

::

  version: 1
  name: python-sample-app
  description: Sample Python web app.
  artifacts:
  - name: python-sample-app
    content:
      href: https://github.com/rackspace-solum-samples/solum-python-sample-app.git
    language_pack: python
    unittest_cmd: pip install -r test-requirements.txt; pep8 app.py
    run_cmd: ./main.sh
    ports: 80

The planfile is used to define the following

1. The git repo where your code exists
2. The languagepack to use
3. A name for your application
4. A command that executes your unittests. This command is executed during the unit test phase of the Solum CI workflow.
5. The port which is exposed publicly for accessing your application.
6. A command that executes your command.


App configuration and environment variables
-------------------------------------------

Applications deployed using solum can be configured using environment variables. Provide a parameter file during application creation to inject environment variables

::

  $ solum app create --plan-file planfile.yaml --param-file params.yaml

In the example above, we pass in the parameter file (shown in the table below) using the --param-file flag.
The parameter file contains key value pairs which are injected into the application run time environment.

::

  key: secret_key
  user: user_name_goes_here
  password: password_for_demo


Set up a Development Environment
--------------------------------

These instructions are for those who plan to contribute to Solum, or use features that are not yet in the latest release.

1. Clone the Solum repo.
At present it is a Stackforge project, and its repository is available on the OpenStack Git server.

::

  $ mkdir ~/Solum
  $ cd Solum
  $ git clone git://git.openstack.org/stackforge/solum

In addition to Solum, your environment will also need Devstack to configure and run the requisite OpenStack components, including Keystone, Glance, Nova, Neutron, and Heat.

Vagrant Dev Environment (optional, for developers)
--------------------------------------------------

2. We have provided a Vagrant environment to deploy Solum and its required OpenStack components via Devstack. We recommend using this approach if you are planning to contribute to Solum. This takes about the same amount of time as setting up Devstack manually, but it automates the setup for you.
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
