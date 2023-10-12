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