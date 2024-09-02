#!/bin/bash

#
# A startup script executed on each user-server spawn authorized
# via LTI containing the custom claim STARTUP_GIT_REPOSITORY.
#
# Globals:
#   STARTUP_GIT_REPOSITORY The Git repository to be cloned on the startup
#   STARTUP_GIT_REPOSITORY_DIR_NAME The directory name of the Git repository to be cloned
#

if [ -n "${STARTUP_GIT_REPOSITORY+x}" ]; then
  git clone "${STARTUP_GIT_REPOSITORY}" "/home/jovyan/work/${STARTUP_GIT_REPOSITORY_DIR_NAME}"
fi

exec jupyterhub-singleuser "$@"
