How to Get Started with Solum
=============================

Installing Solum using devstack
-------------------------------

.. include:: ../../../contrib/devstack/README.rst


Local package installation
--------------------------

Install Solum::

 $ pip install -e .

Run Solum API server::

 $ solum-api

Hit the API server::

 $ curl localhost:9777

Milestone 1 run-through
-----------------------

1. Prepare the build setup:
   ./contrib/lp-cedarish/vm-slug/prepare download-cedarish
2. Install solum using devstack (see above)
3. screen -x (work around no trusts)

 - goto solum-worker (Ctrl-a ")
 - Ctrl-C to stop the process
 - source ../devstack/openrc
 - restart the process
 - (Ctrl-a d) to exit screen

4. solum app create example_plans/ex1.yaml
::

 +-------------+------------------------------------------------------------------------+
 | Property    | Value                                                                  |
 +-------------+------------------------------------------------------------------------+
 | description | Nodejs express.                                                        |
 | uri         | http://192.168.1.67:9777/v1/plans/32fcbf9d-8e88-47a7-9e2a-0705b7cec3a6 |
 | uuid        | 32fcbf9d-8e88-47a7-9e2a-0705b7cec3a6                                   |
 | name        | ex1                                                                    |
 +-------------+------------------------------------------------------------------------+


5. solum assembly create http://192.168.1.67:9777/v1/plans/32fcbf9d-8e88-47a7-9e2a-0705b7cec3a6 --assembly=test
::

 +-------------+--------------------------------------+
 | Property    | Value                                |
 +-------------+--------------------------------------+
 | status      |                                      |
 | description | None                                 |
 | uuid        | ac289a7b-16db-4316-b5c7-085f0905cfd0 |
 | name        | test                                 |
 +-------------+--------------------------------------+
