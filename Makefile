PYTHON ?= python3

# The path to the pubkey to configure the E2E testing instance with.
TEST_PUBKEY ?= ~/.ssh/id_rsa.pub

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


test-deps:
	pip3 install --upgrade ansible -r https://raw.githubusercontent.com/linode/ansible_linode/main/requirements.txt
	ansible-galaxy collection install linode.cloud

# Runs the E2E test suite on a host provisioned by Ansible.
e2e:
	ANSIBLE_HOST_KEY_CHECKING=False ANSIBLE_STDOUT_CALLBACK=debug ansible-playbook -v --extra-vars="debug=${LINODE_DEBUG} ssh_pubkey_path=${TEST_PUBKEY}" ./hack/run-e2e.yml

# Runs the E2E test suite locally.
# NOTE: E2E tests must be run from within a Linode.
e2e-local:
	cd test && make e2e-local-int