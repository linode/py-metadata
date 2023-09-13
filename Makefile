PYTHON ?= python3

@PHONEY: clean
clean:
	mkdir -p dist
	rm -r dist

@PHONEY: build
build: clean requirements
	$(PYTHON) -m build  --wheel --sdist

@PHONEY: requirements
requirements:
	pip install -r requirements.txt