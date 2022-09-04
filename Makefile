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

run-api:  ## Run api
run-api:
	poetry shell
	uvicorn src.main:app --reload