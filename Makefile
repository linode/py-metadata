PYTHON ?= python3
VERSION := ./linode_metadata/version.py

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
	@echo "__version__ = \"${LINODE_METADATA_VERSION}\"\n" > $(VERSION)
