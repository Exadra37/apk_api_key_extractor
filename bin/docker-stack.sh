#!/bin/bash

set -eu

Main() {

  ##############################################################################
  # DEFAULTS
  ##############################################################################

  local IMAGE_NAME=apk_api_key_extractor
  local UBUNTU_DOCKER_TAG="18.04"
  local CONTAINER_USER=$(id -u)
  local COMMAND="developer"
  local BUILD_PATH=./
  local BACKGROUND_MODE="-it"
  local PORT_MAP="7000:5000"


  ##############################################################################
  # PARSE INPUT
  ##############################################################################

  if [ ! -f ./config.yml ]; then
    cp config.example.yml config.yml
  fi

  if [ ! -f ./.env ]; then
    touch ./.env
  fi

  if [ -f ./.env ]; then
    source ./.env
  fi

  for input in "${@}"; do
    case "${input}" in
      --tag )
        UBUNTU_DOCKER_TAG="${2? Missing Python version!!!}"
        shift 2
        ;;

      -d | --detached )
        BACKGROUND_MODE="--detach"
        shift 1
        ;;

      -u | --user )
        CONTAINER_USER=${2? Missing user for container!!!}
        shift 2
        ;;

      build )
        sudo docker build \
          --file "${BUILD_PATH}"/"Dockerfile" \
          --build-arg "TAG=${UBUNTU_DOCKER_TAG}" \
          -t ${IMAGE_NAME} \
          "${BUILD_PATH}"

          exit 0
        ;;

      shell )
        COMMAND=zsh
        shift 1
      ;;
    esac
  done


  ##############################################################################
  # EXECUTION
  ##############################################################################


  sudo docker run \
    --rm \
    --cpus 3 \
    ${BACKGROUND_MODE} \
    --user ${CONTAINER_USER} \
    --env-file .env \
    --volume "${PWD}/../":/home/developer/workspace \
    --volume "${PWD}/apks_analyzed":/home/developer/apks_analyzed \
    --volume "${PWD}/apks_decoded":/home/developer/apks_decoded \
    --volume $PWD/../python-cli/data/apks/:/home/developer/apks \
    "${IMAGE_NAME}" \
    "${COMMAND}" ${@}
}

Main "${@}"
