==========================
Enabling Solum in DevStack
==========================

1. Install Docker version 1.7.0 using following steps (Solum has been tested with this version of Docker)::

    echo deb http://get.docker.com/ubuntu docker main | sudo tee /etc/apt/sources.list.d/docker.list
    sudo apt-key adv --keyserver pgp.mit.edu --recv-keys 36A1D7869245C8950F966E92D8576A8BA88D21E9
    sudo apt-get update
    sudo apt-get install lxc-docker-1.7.0

2. Download DevStack::

    git clone https://opendev.org/openstack/devstack.git
    cd devstack

3. Add this repo as an external repository::

    cat > local.conf <<END
    [[local|localrc]]
    enable_plugin solum https://opendev.org/openstack/solum
    END

   To use stable branches, make sure devstack is on that branch, and specify
   the branch name to enable_plugin, for example::

    enable_plugin solum https://opendev.org/openstack/solum stable/mitaka

4. Run ``./stack.sh``.

.. note::

  This setup will produce virtual machines, not Docker containers.
  For an example of the Docker setup, see::

    https://wiki.openstack.org/wiki/Solum/Docker
