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



test-deps:
	$(PYTHON) -m pip install --upgrade ansible -r https://raw.githubusercontent.com/linode/ansible_linode/main/requirements.txt
	ansible-galaxy collection install linode.cloud

# Runs the E2E test suite on a host provisioned by Ansible.
e2e:
	ANSIBLE_HOST_KEY_CHECKING=False ANSIBLE_STDOUT_CALLBACK=debug ansible-playbook -v --extra-vars="debug=${LINODE_DEBUG} ssh_pubkey_path=${TEST_PUBKEY}" ./hack/run-e2e.yml

# Runs the E2E test suite locally.
# NOTE: E2E tests must be run from within a Linode.
e2e-local:
	cd test && make e2e-local-int