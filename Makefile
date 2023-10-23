PYTHON ?= python3
LINODE_METADATA_VERSION ?= "0.0.0.dev"
VERSION_FILE := ./linode_metadata/version.py

@PHONEY: clean
clean:
	rm -rf dist

@PHONEY: build
build: clean create-version
	$(PYTHON) -m pip install -U build
	$(PYTHON) -m build  --wheel --sdist

@PHONEY: install
install: build
	$(PYTHON) -m pip install dist/*.whl

@PHONEY: create-version
create-version:
	@echo "__version__ = \"${LINODE_METADATA_VERSION}\"" > $(VERSION_FILE)

.PHONY: lint
lint: build
	isort --check-only linode_metadata
	autoflake --check linode_metadata
	black --check --verbose linode_metadata
	pylint linode_metadata

.PHONY: black
black:
	black linode_metadata

.PHONY: isort
isort:
	isort linode_metadata

.PHONY: autoflake
autoflake:
	autoflake linode_metadata

.PHONY: format
format: black isort autoflake
