PYTHON ?= python3
VENV ?= .venv

.PHONY: install init-db dev test generate-icons

install:
	$(PYTHON) -m venv $(VENV)
	$(VENV)/bin/pip install --upgrade pip wheel
	$(VENV)/bin/pip install -r server/requirements.txt

init-db:
	$(VENV)/bin/python server/manage.py init-db

dev:
	$(VENV)/bin/python server/manage.py run-dev

test:
	$(VENV)/bin/python -m unittest discover -s tests -v

generate-icons:
	$(PYTHON) scripts/generate_icons.py

