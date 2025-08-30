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

lint: ## check style with flake8
	flake8 src/jenkins_jobs tests

test: ## run tests quickly with the default Python
	pytest -v

test-all: ## run tests on every Python version with tox
	python -m tox

coverage: ## check code coverage quickly with the default Python
	coverage run --source jenkins_jobs -m pytest
	coverage report -m
	coverage html
	$(BROWSER) htmlcov/index.html

docs: ## generate Sphinx HTML documentation, including API docs
	rm -f docs/jenkins_jobs.rst
	rm -f docs/modules.rst
	sphinx-apidoc --ext-autodoc -o docs/ src/jenkins_jobs
	$(MAKE) -C docs clean
	$(MAKE) -C docs html
	$(BROWSER) docs/_build/html/index.html

servedocs: docs ## compile the docs watching for changes
	watchmedo shell-command -p '*.rst' -c '$(MAKE) -C docs html' -R -D .

release: dist ## package and upload a release
	twine upload dist/*

dist: clean ## builds source and wheel package
	python setup.py sdist
	python setup.py bdist_wheel
	ls -l dist

install: clean ## install the package to the active Python's site-packages
	python setup.py install

init:
	pyenv virtualenv $(VIRTUALENV)
	pyenv local $(VIRTUALENV)
	python -m pip install --upgrade pip wheel setuptools

update-deps:
	python -m pip install --use-pep517 --no-build-isolation -r requirements-dev.txt

debug:
	export JOBS_REPORTER_DATA=$(DATA_SAMPLE) && python -m pdb jobs_reporter.py --user foobar --token foobar --jenkins foobar

run:
	python jobs_reporter.py --user $(USER) --token $(TOKEN) --jenkins $(SERVER)

local:
	export JOBS_REPORTER_DATA=$(DATA_SAMPLE) && python jobs_reporter.py --user foobar --token foobar --jenkins foobar
