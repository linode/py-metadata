PYTHON ?= python3
LINODE_METADATA_VERSION ?= "0.0.0.dev"
VERSION_FILE := ./linode_metadata/version.py

# The path to the pubkey to configure the E2E testing instance with.
TEST_PUBKEY ?= ~/.ssh/id_rsa.pub

VERSION_MODULE_DOCSTRING ?= \"\"\"\nThe version of linode_metadata.\n\"\"\"\n\n

.PHONY: clean
clean:
	rm -rf dist

.PHONY: build
build: clean create-version
	$(PYTHON) -m pip install -U build
	$(PYTHON) -m build  --wheel --sdist

.PHONY: install
install: build
	$(PYTHON) -m pip install dist/*.whl

.PHONY: create-version
create-version:
	@printf "${VERSION_MODULE_DOCSTRING}__version__ = \"${LINODE_METADATA_VERSION}\"\n" > $(VERSION_FILE)

.PHONY: dev-install
dev-install: create-version
	$(PYTHON) -m pip install -e ".[dev]"

.PHONY: test-deps
test-deps:
	$(PYTHON) -m pip install --upgrade ansible -r https://raw.githubusercontent.com/linode/ansible_linode/main/requirements.txt
	ansible-galaxy collection install linode.cloud

# Runs the E2E test suite on a host provisioned by Ansible.
.PHONY: e2e
e2e:
	ANSIBLE_HOST_KEY_CHECKING=False ANSIBLE_STDOUT_CALLBACK=debug ansible-playbook -v --extra-vars="debug=${LINODE_DEBUG} ssh_pubkey_path=${TEST_PUBKEY} cleanup_linode=${CLEANUP_TEST_LINODE_INSTANCE}" ./hack/run-e2e.yml


# Define the timestamp and dynamic report filename
timestamp := $(shell date +'%Y%m%d%H%M')
report_filename:=${timestamp}_py_metadata_test_report.xml

# Runs the E2E test suite locally.
# NOTE: E2E tests must be run from within a Linode.
.PHONY: e2e-local
e2e-local:
	$(PYTHON) -m pytest test/integration/ --junitxml="$(report_filename)"

.PHONY: lint
lint:
	$(PYTHON) -m isort --check-only linode_metadata test
	$(PYTHON) -m autoflake --check linode_metadata test
	$(PYTHON) -m black --check --verbose linode_metadata test
	$(PYTHON) -m pylint linode_metadata

.PHONY: black
black:
	$(PYTHON) -m black linode_metadata test

.PHONY: isort
isort:
	$(PYTHON) -m isort linode_metadata test

.PHONY: autoflake
autoflake:
	$(PYTHON) -m autoflake linode_metadata test

.PHONY: format
format: black isort autoflake

.PHONY: unit-test
unittest:
	$(PYTHON) -m pytest test/unit/