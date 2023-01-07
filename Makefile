LOCAL_TAG:=$(shell date +"%Y-%m-%d-%H-%M")
LOCAL_IMAGE_NAME:=gender-image:v1
# shell is used to avoid the minutes or seconds change while executing
# integration test: if image name is present, dont need to build it again
# publish here is only for show, just echoing

test:
	pytest tests/

quality_checks:
	isort .
	black .
	pylint --recursive=y .

build: quality_checks test
	docker build -t ${LOCAL_IMAGE_NAME} .

# integration_test: build
# 	LOCAL_IMAGE_NAME=${LOCAL_IMAGE_NAME} bash integraton-test/run.sh 

# publish: build integration_test
# 	LOCAL_IMAGE_NAME=${LOCAL_IMAGE_NAME} bash scripts/publish.sh

# setup:
# 	pipenv install --dev
# 	pre-commit install