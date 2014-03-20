if is_service_enabled solum; then
    if [[ "$1" == "source" ]]; then
        source $TOP_DIR/lib/solum
    elif [[ "$1" == "stack" && "$2" == "install" ]]; then
        echo_summary "Installing Solum"
        install_solum
        install_solumclient
    elif [[ "$1" == "stack" && "$2" == "post-config" ]]; then
        echo_summary "Configuring Solum"
        add_solum_user
        configure_solum

        if is_service_enabled key; then
           create_solum_service_and_endpoint
        fi
    elif [[ "$1" == "stack" && "$2" == "extra" ]]; then
        echo_summary "Initializing Solum"
        init_solum
        start_solum
    fi

    if [[ "$1" == "unstack" ]]; then
        stop_solum
    fi
fi
