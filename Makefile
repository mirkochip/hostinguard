#!/bin/bash
VENV_BIN_DIR:="venv/bin"
DEPS:="requirements.txt"
PIP:="$(VENV_BIN_DIR)/pip"
PIP_DOWNLOAD:=".pip_download"
PIP_UPGRADES:=".pip_upgrades"
PYTHON:="$(VENV_BIN_DIR)/python"
TOX:="$(VENV_BIN_DIR)/tox"
PROD_DEPS:="requirements/requirements-base.txt"
ARTIFACT_EXCLUDE:=".git/*" ".gitignore" ".tox/*" ".cache/*" ".coverage/*" ".editorconfig/*" "coverage.xml" ".htmlcov/*" ".docs/*" "venv/*" "setup.cfg" "tox.ini" "src/tests/*" "criluge-api*.tgz" "src/main/params.py" "*.sqlite3" "*.sqlite" ".idea/*" ".pip_download/*" ".pip_upgrades/*"
ARTIFACT=hostinguard.zip

define create-venv
python3.6 -m venv venv
endef

tox: venv
	@$(TOX) -- src/tests

check_forgotten_migrations:
	@$(PYTHON) src/manage.py makemigrations --check --dry-run

coverage_badge:
	rm -f coverage.svg
	coverage-badge -o coverage.svg

pyclean:
	@rm -rf .cache
	@rm -rf htmlcov coverage.xml .coverage
	@find . -name *.pyc -delete
	@find . -type d -name __pycache__ -delete

clean: pyclean
	@rm -rf venv
	@rm -rf .tox
	@rm -rf $(PIP_DOWNLOAD)
	@rm -rf $(ARTIFACT)

venv:
	@$(create-venv)
	@$(PIP) install --upgrade pip
	@$(PIP) install -U setuptools -q
	@$(PIP) install -U pip -q
	@$(PIP) install -r $(DEPS)

test: pyclean venv check_forgotten_migrations tox coverage_badge

build: clean artifact

artifact:
	@$(create-venv)
	@$(PIP) install --upgrade pip
	@$(PIP) install -U setuptools -q
	@$(PIP) download setuptools --dest $(PIP_UPGRADES)
	@$(PIP) download --dest $(PIP_DOWNLOAD) -r $(PROD_DEPS)
	zip -r $(ARTIFACT) ./ -x $(ARTIFACT_EXCLUDE)
	@echo 'Done!'
