The contrib/devstack/ directory contains the files necessary to integrate Solum with devstack.

To install::

    $ DEVSTACK_DIR=.../path/to/devstack
    $ cp lib/solum ${DEVSTACK_DIR}/lib
    $ cp extras.d/70-solum.sh ${DEVSTACK_DIR}/extras.d

Add the following to your local.conf::

    enable_service solum
    enable_service solum-api
    enable_service solum-build-api
    enable_service solum-conductor
    enable_service solum-deployer
    enable_service solum-worker

Run devstack as normal::

    $ cd ${DEVSTACK_DIR}
    $ ./stack.sh
