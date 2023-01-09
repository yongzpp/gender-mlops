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

sudo apt install -y software-properties-common gnupg apt-transport-https ca-certificates
wget -qO - https://www.mongodb.org/static/pgp/server-5.0.asc | sudo apt-key add -
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/5.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-5.0.list
sudo apt update
sudo apt install -y mongodb-org
sudo systemctl start mongod

python ./tests/integration_test.py

ERROR_CODE=$?

if [ ${ERROR_CODE} != 0 ]; then
    docker-compose logs
    docker-compose down
    exit ${ERROR_CODE}
fi

sudo docker-compose down