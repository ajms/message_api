define find.functions
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##//'
endef

help:
	@echo 'The following commands can be used.'
	@echo ''
	$(call find.functions)

test: ## Run pytest
test:
	pytest . -p no:logging -p no:warnings

generate-admin-pw:  ## Generate a hashed admin pw for local exectution
generate-admin-pw:
	python -m src.security

docker-redis:  ## Run redis for development mode
docker-redis:
	docker compose -f docker/redis.yml up -d

run-api:  ## Run api
run-api:
	poetry run uvicorn src.main:app --reload

requirements:  ## Create requirements for docker
requirements:
	poetry export -f requirements.txt --without-hashes --output requirements.txt

build-base-image:
build-base-image:  ## Build base image
	docker build . -f docker/Dockerfile.base -t message-api-base:v0.1.0

build-images:
build-images:  ## Build images
	docker build . -f docker/Dockerfile -t message-api:v0.1.0 --build-arg BASEIMAGE=message-api-base:v0.1.0
	docker build . -f docker/Dockerfile.qr -t message-api-qr:v0.1.0 --build-arg BASEIMAGE=message-api-base:v0.1.0
	docker build . -f docker/Dockerfile.messages -t message-api-messages:v0.1.0 --build-arg BASEIMAGE=message-api-base:v0.1.0

docker-run:  ## Run docker-compose
docker-run:
	docker compose --env-file .env.docker -f docker/message-api.yml down
	docker compose --env-file .env.docker -f docker/message-api.yml up -d
