The contrib/devstack/ directory contains the files necessary to integrate Solum with devstack.

To install::

    $ DEVSTACK_DIR=.../path/to/devstack
    $ cp lib/solum ${DEVSTACK_DIR}/lib
    $ cp extras.d/70-solum.sh ${DEVSTACK_DIR}/extras.d

To configure devstack to run solum::

    $ cd ${DEVSTACK_DIR}
    $ echo "enable_service solum" >> localrc

Run devstack as normal::

    $ ./stack.sh
