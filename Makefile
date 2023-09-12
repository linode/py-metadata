PYTHON ?= python3

@PHONEY: clean
clean:
	mkdir -p dist
	rm -r dist

@PHONEY: build
build: clean
	$(PYTHON) -m build  --wheel --sdist