# The ports that user containers will be asked to use to expose their Reboot
# servers.
USER_CONTAINER_GRPC_PORT = 50051
USER_CONTAINER_WEBSOCKET_PORT = 50052
USER_CONTAINER_HTTP_PORT = 50053

# The reboot system namespace (used by admin auth when an application
# runs on a Reboot Cloud).
REBOOT_SYSTEM_NAMESPACE = 'reboot-system'

# The hostname that clients on a Reboot Cloud use when they want to talk
# to any Reboot service.
REBOOT_ROUTABLE_HOSTNAME = 'reboot-service'

### Environment variables.
# We use environment variables when we need to communicate information between
# processes. Our naming convention is as follows:
#   `ENVVAR_<SOMETHING>` is the name of an environment variable.
#   `<SOMETHING>_<VALUE-NAME>` is one VALUE the `SOMETHING` environment
#    variable might take.

# Space ID injected via an environment variable.
ENVVAR_REBOOT_SPACE_ID = 'REBOOT_SPACE_ID'
# Application ID injected via an environment variable.
ENVVAR_REBOOT_APPLICATION_ID = 'REBOOT_APPLICATION_ID'
# Consensus ID injected via an environment variable.
ENVVAR_REBOOT_CONSENSUS_ID = 'REBOOT_CONSENSUS_ID'

# Gives the mode in which a Reboot application is expected to be started.
ENVVAR_REBOOT_MODE = 'REBOOT_MODE'
REBOOT_MODE_CONFIG = 'config'  # Start the server as a config server.

# Gives the port on which a config-mode server is expected to start serving.
ENVVAR_REBOOT_CONFIG_SERVER_PORT = 'REBOOT_CONFIG_SERVER_PORT'

# Gives the port on which an `rbt serve` application is expected to serve its
# application.
ENVVAR_PORT = 'PORT'

ENVVAR_RBT_PORT = 'RBT_PORT'

# The application ID of the Reboot application hosting the `AdminAuth` service.
ENVVAR_REBOOT_ADMIN_AUTH_APPLICATION_ID = 'REBOOT_ADMIN_AUTH_APPLICATION_ID'
