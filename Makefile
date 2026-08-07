VIRTUALENV:=$(shell basename $$PWD)
.PHONY: clean clean-test clean-pyc clean-build docs help
.DEFAULT_GOAL := help

SPHINX_APIDOC_OPTIONS:=members,undoc-members,show-inheritance,private-members,special-members

define BROWSER_PYSCRIPT
import os, webbrowser, sys

from urllib.request import pathname2url

webbrowser.open("file://" + pathname2url(os.path.abspath(sys.argv[1])))
endef
export BROWSER_PYSCRIPT

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

BROWSER := python -c "$$BROWSER_PYSCRIPT"

help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

clean: clean-build clean-pyc clean-test ## remove all build, test, coverage and Python artifacts

clean-build: ## remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' | xargs rm -rf
	find . -name '*.egg' | xargs rm -rf

clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' | xargs rm -rf
	find . -name '*.pyo' | xargs rm -rf
	find . -name '*~' | xargs rm -rf
	find . -name '__pycache__' | xargs rm -rf

clean-test: ## remove test and coverage artifacts
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/
	rm -fr .pytest_cache

lint: ## check style with ruff
	uv run ruff check src/jenkins_jobs tests

test: ## run tests quickly with the default Python
	uv run pytest -v

test-all: ## run tests on every Python version with tox
	uv run tox

coverage: ## check code coverage quickly with the default Python
	uv run coverage run --source jenkins_jobs -m pytest
	uv run coverage report -m
	uv run coverage html
	$(BROWSER) htmlcov/index.html

docs: ## generate Sphinx HTML documentation, including API docs
	rm -f docs/jenkins_jobs.rst
	rm -f docs/modules.rst
	uv run sphinx-apidoc --ext-autodoc -o docs/ src/jenkins_jobs
	$(MAKE) -C docs clean
	$(MAKE) -C docs html
	$(BROWSER) docs/_build/html/index.html

serverdocs: docs ## compile the docs watching for changes
	watchmedo shell-command -p '*.rst' -c '$(MAKE) -C docs html' -R -D .

release: dist ## package and upload a release
	uv publish

dist: clean ## builds source and wheel package
	uv build
	ls -l dist

install: clean ## install the package to the active Python's site-packages
	uv pip install .

init: ## create the uv-managed virtualenv and install all dependencies
	uv venv
	uv sync --extra dev

update-deps: ## refresh uv.lock to the latest allowed versions and reinstall
	uv lock --upgrade
	uv sync --extra dev

debug:
	uv run python -m pdb -m jenkins_jobs.reporter --shelve-file $(DATA_SAMPLE)

run:
	uv run jenkins_jobs --user $(USER) --token $(TOKEN) --jenkins $(SERVER)

local:
	uv run jenkins_jobs --shelve-file $(DATA_SAMPLE)
