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

docker-redis:  ## Run redis
docker-redis:
	docker-compose -f docker/redis.yml up -d

run-api:  ## Run api
run-api:
	poetry run uvicorn src.main:app --reload
