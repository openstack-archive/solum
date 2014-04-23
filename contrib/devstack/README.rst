The contrib/devstack/ directory contains the files necessary to integrate Solum with devstack.

To install::

    $ DEVSTACK_DIR=.../path/to/devstack
    $ cp lib/solum ${DEVSTACK_DIR}/lib
    $ cp extras.d/70-solum.sh ${DEVSTACK_DIR}/extras.d

Add the following to your local.conf::

    disable_service n-net
    enable_service q-svc
    enable_service q-agt
    enable_service q-dhcp
    enable_service q-l3
    enable_service q-meta
    enable_service neutron

    enable_service solum
    enable_service solum-api
    enable_service solum-build-api
    enable_service solum-conductor
    enable_service solum-deployer
    enable_service solum-worker

Declare SOLUM_INSTALL_CEDARISH to automatically install cedarish LangPack::

    export SOLUM_INSTALL_CEDARISH=True

To use docker image format::

    export SOLUM_IMAGE_FORMAT='docker'

Run devstack as normal::

    $ cd ${DEVSTACK_DIR}
    $ ./stack.sh
