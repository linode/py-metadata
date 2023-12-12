PYTHON ?= python3
LINODE_METADATA_VERSION ?= "0.0.0.dev"
VERSION_FILE := ./linode_metadata/version.py

# The path to the pubkey to configure the E2E testing instance with.
TEST_PUBKEY ?= ~/.ssh/id_rsa.pub

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

@PHONEY: dev-install
dev-install: create-version
	$(PYTHON) -m pip install -e ".[dev]"

test-deps:
	$(PYTHON) -m pip install --upgrade ansible -r https://raw.githubusercontent.com/linode/ansible_linode/main/requirements.txt
	ansible-galaxy collection install linode.cloud

# Runs the E2E test suite on a host provisioned by Ansible.
e2e:
	ANSIBLE_HOST_KEY_CHECKING=False ANSIBLE_STDOUT_CALLBACK=debug ansible-playbook -v --extra-vars="debug=${LINODE_DEBUG} ssh_pubkey_path=${TEST_PUBKEY} cleanup_linode=${CLEANUP_TEST_LINODE_INSTANCE}" ./hack/run-e2e.yml

# Runs the E2E test suite locally.
# NOTE: E2E tests must be run from within a Linode.
e2e-local:
	$(PYTHON) -m pytest test/integration/

.PHONY: lint
lint: build
	$(PYTHON) -m isort --check-only linode_metadata test
	$(PYTHON) -m autoflake --check linode_metadata test
	$(PYTHON) -m black --check --verbose linode_metadata test
	$(PYTHON) -m pylint linode_metadata test

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
