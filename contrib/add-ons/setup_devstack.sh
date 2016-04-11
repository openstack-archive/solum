#!/bin/sh

SOLUM_DIR="${HOME}/solum"
DEVSTACK_DIR="${HOME}/devstack"

echo "Checking for Docker"
if [ ! -f /usr/bin/docker ] ; then
	echo "This setup requires docker. See: README.rst"
	exit 1
fi

echo "Getting Solum Code"
mkdir -p ${SOLUM_DIR}
git clone git://git.openstack.org/openstack/solum ${SOLUM_DIR}

echo "Getting Devstack Code"
mkdir -p ${DEVSTACK_DIR}
git clone https://git.openstack.org/openstack-dev/devstack.git ${DEVSTACK_DIR}

echo "Setting up Devstack for Solum"
cd ${SOLUM_DIR}/contrib/devstack
cp lib/solum ${DEVSTACK_DIR}/lib
cp extras.d/70-solum.sh ${DEVSTACK_DIR}/extras.d
cp local.conf ${DEVSTACK_DIR}

echo "Starting Devstack"
cd ${DEVSTACK_DIR} && ./stack.sh

echo "Finished!"
