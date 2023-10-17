PYTHON ?= python3

@PHONEY: clean
clean:
	rm -rf dist

@PHONEY: build
build: clean
	$(PYTHON) -m pip install -U build
	$(PYTHON) -m build  --wheel --sdist

@PHONEY: install
install: build
	pip install dist/*.whl

@PHONEY: requirements
requirements:
	$(PYTHON) -m pip install -r requirements.txt

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
