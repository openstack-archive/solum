#!/usr/bin/env/ bash
# Plugin file for Solum services
#-------------------------------

# Dependencies:
# ``functions`` file
# ``DEST``, ``DATA_DIR``, ``STACK_USER`` must be defined
# ``ADMIN_{TENANT_NAME|PASSWORD}`` must be defined

# ``stack.sh`` calls the entry points in this order:
#
# install_solum
# install_solumclient
# configure_solum
# start_solum
# stop_solum

# Save trace setting
XTRACE=$(set +o | grep xtrace)
set -o xtrace

# Defaults
# --------

GITREPO["solum-dashboard"]=${SOLUMDASHBOARD_REPO:-${GIT_BASE}/openstack/solum-dashboard.git}
GITBRANCH["solum-dashboard"]=${SOLUMDASHBOARD_BRANCH:-master}
GITDIR["solum-dashboard"]=$DEST/solum-dashboard

# Support entry points installation of console scripts
if [[ -d $SOLUM_DIR/bin ]]; then
    SOLUM_BIN_DIR=$SOLUM_DIR/bin
else
    SOLUM_BIN_DIR=$(get_python_exec_prefix)
fi

# Toggle for deploying Solum-API under HTTPD + mod_wsgi
SOLUM_USE_MOD_WSGI=${SOLUM_USE_MOD_WSGI:-False}

# Toggle for deploying Solum-API under uwsgi
SOLUM_USE_UWSGI=${SOLUM_USE_UWSGI:-True}

SOLUM_UWSGI=$SOLUM_BIN_DIR/solum-wsgi-api
SOLUM_UWSGI_CONF=$SOLUM_CONF_DIR/solum-api-uwsgi.ini

if [[ "$SOLUM_USE_UWSGI" == "True" ]]; then
    SOLUM_API_URL="$SOLUM_SERVICE_PROTOCOL://$SOLUM_SERVICE_HOST/application_deployment"
else
    SOLUM_API_URL="$SOLUM_SERVICE_PROTOCOL://$SOLUM_SERVICE_HOST:$SOLUM_SERVICE_PORT"
fi

# Functions
# ---------

# create_solum_service_and_endpoint() - Set up required solum service and endpoint
function create_solum_service_and_endpoint() {
    SOLUM_UPDATE_ROLE=$(get_or_create_role "solum_assembly_update")

    # Give the role to the demo and admin users so they can use git push
    # in either of the projects created by devstack
    get_or_add_user_project_role $SOLUM_UPDATE_ROLE demo demo
    get_or_add_user_project_role $SOLUM_UPDATE_ROLE admin demo
    get_or_add_user_project_role $SOLUM_UPDATE_ROLE admin admin

    SOLUM_SERVICE=$(get_or_create_service "solum" "application_deployment" "Solum Service")
    get_or_create_endpoint "application_deployment" \
        "$REGION_NAME" \
        "$SOLUM_API_URL" \
        "$SOLUM_API_URL" \
        "$SOLUM_API_URL"

    SOLUM_BUILDER_SERVICE=$(get_or_create_service "solum" "image_builder" "Solum Image Builder")
    get_or_create_endpoint "image_builder" \
        "$REGION_NAME" \
        "$SOLUM_SERVICE_PROTOCOL://$SOLUM_SERVICE_HOST:$SOLUM_BUILDER_SERVICE_PORT" \
        "$SOLUM_SERVICE_PROTOCOL://$SOLUM_SERVICE_HOST:$SOLUM_BUILDER_SERVICE_PORT" \
        "$SOLUM_SERVICE_PROTOCOL://$SOLUM_SERVICE_HOST:$SOLUM_BUILDER_SERVICE_PORT"
}

# configure_nova_docker - Set config files, create data dirs, etc
function configure_nova_docker {
    iniset $NOVA_CONF DEFAULT compute_driver zun.DockerDriver

    # CentOS/RedHat distros don't start the services just after the package
    # is installed if it is not explicitily set. So the script fails on
    # them in this killall because there is nothing to kill.
    sudo killall docker || true

    # Enable debug level logging
    if [ -f "/etc/default/docker" ]; then
        sudo cat /etc/default/docker
        sudo sed -i 's/^.*DOCKER_OPTS=.*$/DOCKER_OPTS=\"--debug --storage-opt dm.override_udev_sync_check=true\"/' /etc/default/docker
        sudo cat /etc/default/docker
    fi
    if [ -f "/etc/sysconfig/docker" ]; then
        sudo cat /etc/sysconfig/docker
        sudo sed -i 's/^.*OPTIONS=.*$/OPTIONS=--debug --selinux-enabled/' /etc/sysconfig/docker
        sudo cat /etc/sysconfig/docker
    fi
    if [ -f "/usr/lib/systemd/system/docker.service" ]; then
        sudo cat /usr/lib/systemd/system/docker.service
        sudo sed -i 's/docker daemon/docker daemon --debug/' /usr/lib/systemd/system/docker.service
        sudo cat /usr/lib/systemd/system/docker.service
        sudo systemctl daemon-reload
    fi

    sudo service docker start || true

    # setup rootwrap filters
    local rootwrap_conf_src_dir="$ZUN_PROJ_DIR/contrib/nova-docker/etc/nova"
    sudo install -o root -g root -m 644 $rootwrap_conf_src_dir/rootwrap.d/*.filters /etc/nova/rootwrap.d

    cp -r $ZUN_PROJ_DIR/contrib/nova-docker/nova $SOLUM_DIR
    setup_develop $SOLUM_DIR
}

# configure_solum() - Set config files, create data dirs, etc
function configure_solum() {

    # configure_nova_docker

    if [[ ! -d $SOLUM_CONF_DIR ]]; then
        sudo mkdir -p $SOLUM_CONF_DIR
    fi
    sudo chown $STACK_USER $SOLUM_CONF_DIR

    # To support private github repos, do not perform host key check for github.com
    # Need this change on solum-worker instances
    STACK_USER_SSH_DIR=/home/$STACK_USER/.ssh
    if [[ ! -d $STACK_USER_SSH_DIR ]]; then
        sudo mkdir -p $STACK_USER_SSH_DIR
    fi
    sudo chown $STACK_USER $STACK_USER_SSH_DIR
    echo -e "Host github.com\n\tStrictHostKeyChecking no\n" > $STACK_USER_SSH_DIR/config

    # config solum rootwrap
    configure_rootwrap solum

    # Generate sample config and configure common parameters.
    mkdir -p /tmp/solum

    pushd $SOLUM_DIR
        oslo-config-generator --config-file=${SOLUM_DIR}/etc/solum/config-generator.conf --output-file=/tmp/solum/solum.conf.sample
    popd
    cp /tmp/solum/solum.conf.sample $SOLUM_CONF_DIR/$SOLUM_CONF_FILE

    iniset $SOLUM_CONF_DIR/$SOLUM_CONF_FILE DEFAULT debug $SOLUM_DEBUG

    iniset $SOLUM_CONF_DIR/$SOLUM_CONF_FILE DEFAULT use_syslog $SYSLOG

    # make trace visible
    iniset $SOLUM_CONF_DIR/$SOLUM_CONF_FILE DEFAULT logging_context_format_string "%(asctime)s.%(msecs)03d %(process)d %(levelname)s %(name)s [%(request_id)s %(user_identity)s] %(instance)s%(message)s"

    # Setup keystone_authtoken section
    configure_auth_token_middleware $SOLUM_CONF_DIR/$SOLUM_CONF_FILE $SOLUM_USER $SOLUM_AUTH_CACHE_DIR
    iniset $SOLUM_CONF_DIR/$SOLUM_CONF_FILE keystone_authtoken www_authenticate_uri $KEYSTONE_AUTH_URI

    # configure the database.
    iniset $SOLUM_CONF_DIR/$SOLUM_CONF_FILE database connection `database_connection_url solum`

    # configure worker lp operator user/password
    iniset $SOLUM_CONF_DIR/$SOLUM_CONF_FILE worker lp_operator_user $SOLUM_USER
    iniset $SOLUM_CONF_DIR/$SOLUM_CONF_FILE worker lp_operator_password $SERVICE_PASSWORD
    iniset $SOLUM_CONF_DIR/$SOLUM_CONF_FILE worker lp_operator_tenant_name service

    # configure the api servers to listen on
    iniset $SOLUM_CONF_DIR/$SOLUM_CONF_FILE api host $(ipv6_unquote $SOLUM_SERVICE_HOST)
    iniset $SOLUM_CONF_DIR/$SOLUM_CONF_FILE api port $SOLUM_SERVICE_PORT
    iniset $SOLUM_CONF_DIR/$SOLUM_CONF_FILE builder host $(ipv6_unquote $SOLUM_SERVICE_HOST)
    iniset $SOLUM_CONF_DIR/$SOLUM_CONF_FILE builder port $SOLUM_BUILDER_SERVICE_PORT

    # configure assembly handler to create appropriate image format
    iniset $SOLUM_CONF_DIR/$SOLUM_CONF_FILE api image_format $SOLUM_IMAGE_FORMAT

    # common rpc settings
    iniset_rpc_backend solum $SOLUM_CONF_DIR/$SOLUM_CONF_FILE DEFAULT

    # service rpc settings
    iniset $SOLUM_CONF_DIR/$SOLUM_CONF_FILE conductor topic solum-conductor
    iniset $SOLUM_CONF_DIR/$SOLUM_CONF_FILE deployer topic solum-deployer
    iniset $SOLUM_CONF_DIR/$SOLUM_CONF_FILE deployer handler heat
    iniset $SOLUM_CONF_DIR/$SOLUM_CONF_FILE worker topic solum-worker
    iniset $SOLUM_CONF_DIR/$SOLUM_CONF_FILE worker handler shell
    iniset $SOLUM_CONF_DIR/$SOLUM_CONF_FILE worker proj_dir $SOLUM_PROJ_DIR

    iniset $SOLUM_CONF_DIR/$SOLUM_CONF_FILE deployer max_attempts $SOLUM_MAX_ATTEMPTS
    iniset $SOLUM_CONF_DIR/$SOLUM_CONF_FILE deployer wait_interval $SOLUM_WAIT_INTERVAL
    iniset $SOLUM_CONF_DIR/$SOLUM_CONF_FILE deployer growth_factor $SOLUM_GROWTH_FACTOR

    # configure AllHostsFilter in /etc/nova/nova.conf
    iniset $NOVA_CONF_DIR/$NOVA_CONF_FILE DEFAULT scheduler_default_filters AllHostsFilter

    if [[ $SOLUM_IMAGE_FORMAT == 'vm' ]]; then
        # configure Virtdriver in /etc/nova/nova.conf
        iniset $NOVA_CONF_DIR/$NOVA_CONF_FILE DEFAULT compute_driver libvirt.LibvirtDriver
        #solum_install_start_docker_registry
        solum_install_core_os
    else
        echo "SOLUM_IMAGE_FORMAT docker or vm"
    fi

    if [[ "$USE_PYTHON3" = "True" ]]; then
        # Switch off glance->swift communication as swift fails under py3.x
        iniset /etc/glance/glance-api.conf glance_store default_store file
    fi

    if [ "$SOLUM_USE_MOD_WSGI" == "True" ]; then
        _config_solum_apache_wsgi
    fi

    if [ "$SOLUM_USE_UWSGI" == "True" ]; then
        write_uwsgi_config "$SOLUM_UWSGI_CONF" "$SOLUM_UWSGI" "/application_deployment"
    fi

}

#register solum user in Keystone
function add_solum_user() {

    create_service_user "solum" "admin"

}

function add_additional_solum_users() {

    SOLUM_UPDATE_ROLE=$(get_or_create_role "solum_assembly_update")

    for _LETTER in a b c; do
        local TENANTNAME=solum_tenant_$_LETTER
        get_or_create_project "$TENANTNAME" "default"

        local USERNAME=solum_user_$_LETTER
        get_or_create_user "$USERNAME" "solum" "default"

        get_or_add_user_project_role "$SOLUM_UPDATE_ROLE" "$USERNAME" "$TENANTNAME"
        get_or_add_user_project_role "$SOLUM_UPDATE_ROLE" "admin" "$TENANTNAME"

    done
}

#create_solum_cache_dir() - Setup keystone signing folder
function create_solum_cache_dir() {
    sudo mkdir -p $SOLUM_AUTH_CACHE_DIR
    sudo chown $STACK_USER $SOLUM_AUTH_CACHE_DIR
    sudo chmod 700 $SOLUM_AUTH_CACHE_DIR
    rm -f $SOLUM_AUTH_CACHE_DIR/*
}

# init_solum() - Initialize databases, etc.
function init_solum() {
    recreate_database solum utf8
    # Run Solum db migrations
    solum-db-manage --config-file $SOLUM_CONF_DIR/$SOLUM_CONF_FILE upgrade head
    create_solum_cache_dir

    # NOTE (devkulkarni): Barbican is causing failures such as below
    # http://logs.openstack.org/33/206633/2/check/gate-solum-devstack-dsvm/933cbc3/logs/devstacklog.txt.gz#_2015-08-03_17_13_40_858
    # So temorarily commenting out barbican related code below.

    # if is_service_enabled barbican; then
    #    # Fix barbican configuration
    #    BARBICAN_API_CONF="/etc/barbican/barbican.conf"
    #    BARBICAN_HOST_HREF=$(iniget $BARBICAN_API_CONF DEFAULT host_href)
    #    BARBICAN_HOST_HREF=${BARBICAN_HOST_HREF/localhost/$SERVICE_HOST}
    #    iniset $BARBICAN_API_CONF DEFAULT host_href $BARBICAN_HOST_HREF
    #    if is_running barbican; then
    #        # NOTE(ravips): barbican.{pid,failure} is removed to overcome current
    #        # limitations of stop_barbican. stop_barbican calls screen_stop() only
    #        # to remove the pid but not to kill the process and this causes pkill
    #        # in screen_stop to return non-zero exit code which is trapped by
    #        # devstack/stack.sh
    #        if [ -f $SERVICE_DIR/$SCREEN_NAME/barbican.pid ]; then
    #            rm $SERVICE_DIR/$SCREEN_NAME/barbican.pid
    #        fi
    #        stop_barbican
    #        if [ -f $SERVICE_DIR/$SCREEN_NAME/barbican.failure ]; then
    #            rm $SERVICE_DIR/$SCREEN_NAME/barbican.failure
    #        fi
    #        start_barbican
    #    fi
    # fi
}

# install_solumclient() - Collect source and prepare
function install_solumclient {
    if use_library_from_git "python-solumclient"; then
        git_clone_by_name "python-solumclient"
        setup_dev_lib "python-solumclient"
    else
        pip_install_gr python-solumclient
    fi
}

# install_solum() - Collect source and prepare
function install_solum() {
    # Install package requirements
    install_package expect

    git_clone $SOLUM_REPO $SOLUM_DIR $SOLUM_BRANCH

    setup_develop $SOLUM_DIR

    if [ "$SOLUM_USE_MOD_WSGI" == "True" ]; then
        install_apache_wsgi
    fi

}

function install_solum_dashboard() {
    git_clone_by_name "solum-dashboard"
    setup_dev_lib "solum-dashboard"
    if [ ! -f $HORIZON_DIR/openstack_dashboard/local/enabled/_50_solum.py ] ; then
      ln -s $DEST/solum-dashboard/solumdashboard/local/enabled/_50_solum.py $HORIZON_DIR/openstack_dashboard/local/enabled/_50_solum.py
    fi
    restart_apache_server
}

function cleanup_solum_dashboard() {
    rm $HORIZON_DIR/openstack_dashboard/local/enabled/_50_solum.py
}

# cleanup_solum_apache_wsgi() - Remove wsgi files, disable and remove apache vhost file
function cleanup_solum_apache_wsgi {
    sudo rm -f $(apache_site_config_for solum-api)
}

# _config_solum_apache_wsgi() - Set WSGI config files of Solum
function _config_solum_apache_wsgi {

    local solum_apache_conf=$(apache_site_config_for solum-api)
    local solum_api_port=$SOLUM_SERVICE_PORT
    local venv_path=""

    sudo cp $SOLUM_FILES_DIR/apache-solum-api.template $solum_apache_conf
    sudo sed -e "
        s|%PUBLICPORT%|$solum_api_port|g;
        s|%APACHE_NAME%|$APACHE_NAME|g;
        s|%SOLUM_BIN_DIR%|$SOLUM_BIN_DIR|g;
        s|%API_WORKERS%|$API_WORKERS|g;
        s|%USER%|$STACK_USER|g;
        s|%VIRTUALENV%|$venv_path|g
    " -i $solum_apache_conf
}

# start_solum() - Start running processes, including screen
function start_solum() {
    local enabled_site_file=$(apache_site_config_for solum-api)
    if [ -f ${enabled_site_file} ] && [ "$SOLUM_USE_MOD_WSGI" == "True" ]; then
        enable_apache_site solum-api
        restart_apache_server
        tail_log solum-api /var/log/$APACHE_NAME/solum-api.log
    elif [ "$SOLUM_USE_UWSGI" == "True" ]; then
        run_process solum-api "$(which uwsgi) --ini $SOLUM_UWSGI_CONF"
    else
        run_process solum-api "$SOLUM_BIN_DIR/solum-api --config-file $SOLUM_CONF_DIR/$SOLUM_CONF_FILE"
    fi
    run_process solum-conductor "$SOLUM_BIN_DIR/solum-conductor --config-file $SOLUM_CONF_DIR/$SOLUM_CONF_FILE"
    run_process solum-deployer "$SOLUM_BIN_DIR/solum-deployer --config-file $SOLUM_CONF_DIR/$SOLUM_CONF_FILE"
    run_process solum-worker "$SOLUM_BIN_DIR/solum-worker --config-file $SOLUM_CONF_DIR/$SOLUM_CONF_FILE"
}

# stop_solum() - Stop running processes
function stop_solum() {
    # Kill the solum screen windows
    if [ "$SOLUM_USE_UWSGI" == "True" ]; then
        disable_apache_site solum-api
        restart_apache_server
    else
        stop_process solum-api
    fi
    stop_process solum-conductor
    stop_process solum-deployer
    stop_process solum-worker

    if [[ $SOLUM_IMAGE_FORMAT == 'vm' ]]; then
        solum_stop_docker_registry
    fi
}

# install_docker_registry() - Install and Start Docker Registry
# -------------------------------------------------------------
solum_install_start_docker_registry() {

 # install dependencies
   sudo apt-get update
   sudo apt-get -y install build-essential python-dev libevent-dev python-pip liblzma-dev git libssl-dev python-m2crypto swig

 # clone docker registry
   if [ ! -d /opt/docker-registry ] ; then
      sudo git clone https://github.com/dotcloud/docker-registry.git /opt/docker-registry
   fi
   pushd /opt/docker-registry
   sudo  pip install -r requirements/main.txt
   popd

 # install docker registry
   pip_command=`which pip`
   pip_build_tmp=$(mktemp --tmpdir -d pip-build.XXXXX)
   sudo $pip_command install /opt/docker-registry --build=${pip_build_tmp}

 # initialize config file
   sudo cp /opt/docker-registry/docker_registry/lib/../../config/config_sample.yml /opt/docker-registry/docker_registry/lib/../../config/config.yml

 # start docker registry
   gunicorn --access-logfile - --debug -k gevent -b 0.0.0.0:5042 -w 1 docker_registry.wsgi:application &

}

solum_stop_docker_registry() {
    stop_process docker-registry
    rm -rf ${PIP_BUILD_TMP}
}

solum_install_core_os() {
  wget https://stable.release.core-os.net/amd64-usr/current/coreos_production_openstack_image.img.bz2
  bunzip2 coreos_production_openstack_image.img.bz2
  glance image-create --name coreos --container-format bare --disk-format qcow2 --file coreos_production_openstack_image.img
}


# Main dispatcher
#----------------

if is_service_enabled solum-api solum-conductor solum-deployer solum-worker; then
    if [[ "$1" == "stack" && "$2" == "install" ]]; then
        echo_summary "Installing Solum"
        install_solum
        install_solumclient
        if is_service_enabled horizon; then
            echo_summary "Installing Solum Dashboard"
            install_solum_dashboard
        fi
    elif [[ "$1" == "stack" && "$2" == "post-config" ]]; then
        echo_summary "Configuring Solum"
        add_solum_user
        configure_solum

        if is_service_enabled key; then
           create_solum_service_and_endpoint
        fi
        add_additional_solum_users
    elif [[ "$1" == "stack" && "$2" == "extra" ]]; then
        echo_summary "Initializing Solum"
        init_solum
        start_solum
    fi

    if [[ "$1" == "unstack" ]]; then
        stop_solum
        if [ "$SOLUM_USE_MOD_WSGI" == "True" ]; then
            cleanup_solum_apache_wsgi
        fi
        if [[ "$SOLUM_USE_UWSGI" == "True" ]]; then
            remove_uwsgi_config "$SOLUM_UWSGI_CONF" "$SOLUM_UWSGI"
        fi
        if is_service_enabled horizon; then
            echo_summary "Cleaning Solum Dashboard up"
            cleanup_solum_dashboard
        fi
    fi
fi


# Restore xtrace
$XTRACE

# Local variables:
# mode: shell-script
# End:
