#!/usr/bin/env bash

# if [[ -z "${GITHUB_ACTIONS}" ]]; then
#   cd "$(dirname "$0")"
# fi

# if [ "${LOCAL_IMAGE_NAME}" == "" ]; then
#     LOCAL_TAG=`date +"%Y-%m-%d-%H-%M"`
#     export LOCAL_IMAGE_NAME="stream-model-duration:${LOCAL_TAG}"
#     echo "LOCAL_IMAGE_NAME is not set, building a new image with tag ${LOCAL_IMAGE_NAME}"
#     docker build -t ${LOCAL_IMAGE_NAME} ..
# else
#     echo "no need to build image ${LOCAL_IMAGE_NAME}"
# fi

sudo docker-compose up -d

sleep 5

python ./tests/integration_test.py

ERROR_CODE=$?

if [ ${ERROR_CODE} != 0 ]; then
    docker-compose logs
    docker-compose down
    exit ${ERROR_CODE}
fi

sudo docker-compose down