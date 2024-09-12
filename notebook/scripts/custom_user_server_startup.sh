#!/bin/bash

#
# A startup script executed on each user-server spawn authorized via LTI containing custom claims.
#
# Globals:
#   RESOURCE_NAME A unique name that identifies the resource transferred to the working directory
#   STARTUP_GIT_REPOSITORY The Git repository to be cloned on the startup
#   STARTUP_GIT_REPOSITORY_DIR_NAME The directory name of the Git repository to be cloned
#

CURRENT_TIMESTAMP="$(date +%s)"
RESOURCE_TARGET_NAME="${RESOURCE_NAME:-$CURRENT_TIMESTAMP}"
INSTRUCTOR_RESOURCE_DIR="/home/jovyan/instructor_volume/${RESOURCE_TARGET_NAME}"
STUDENT_RESOURCE_DIR="/home/jovyan/work/${RESOURCE_TARGET_NAME}"

# Synchronize student's resources with instructor's resources from the read-only volume.
mkdir -p "${INSTRUCTOR_RESOURCE_DIR}"
if [ -d "${INSTRUCTOR_RESOURCE_DIR}" ] && ! [ -e "${STUDENT_RESOURCE_DIR}" ]; then
  mkdir -p "${STUDENT_RESOURCE_DIR}"
  cp -a "${INSTRUCTOR_RESOURCE_DIR}"/. "${STUDENT_RESOURCE_DIR}"
fi


# Clone a new and locally non-existing git repositories, if STARTUP_GIT_REPOSITORY* parameters are used.
if [ -n "${STARTUP_GIT_REPOSITORY+x}" ]; then
  git clone "${STARTUP_GIT_REPOSITORY}" "/home/jovyan/work/${STARTUP_GIT_REPOSITORY_DIR_NAME}"
fi

exec jupyterhub-singleuser "$@"
