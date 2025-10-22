.PHONY: update-deps
update-deps:
	pip install --upgrade pip-tools pip setuptools
	#pip-compile --upgrade  --allow-unsafe --resolver=backtracking --build-isolation --generate-hashes --output-file requirements/dev.txt requirements/dev.in

# Useful for testing against a Git version of Safir.
.PHONY: update-deps-no-hashes
update-deps-no-hashes:
	pip install --upgrade pip-tools pip setuptools
	#pip-compile --upgrade --resolver=backtracking --build-isolation --allow-unsafe --output-file requirements/dev.txt requirements/dev.in

.PHONY: init
init:
	pip install --editable .
	#pip install --upgrade
	rm -rf .tox
	pip install --upgrade pre-commit tox
	pre-commit install

.PHONY: update
update: update-deps init

.PHONY: run
run:
	tox run -e run

clean:
	rm -rf build
