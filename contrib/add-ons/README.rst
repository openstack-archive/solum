The contrib/devstack/ directory contains the files necessary to integrate Solum with devstack.

Install Docker, to be used by our build service: http://docs.docker.io/installation/

To install devstack, run the setup script provided in the Solum code tree::

    export SOLUM_DIR=/path/to/solum/source/dir
    sh ${SOLUM_DIR}/contrib/devstack/setup_devstack.sh

Note that this setup will produce virtual machines, not Docker containers.
For an example of the Docker setup, see: https://wiki.openstack.org/wiki/Solum/Docker
