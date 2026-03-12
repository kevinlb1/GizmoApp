PYTHON ?= python3
VENV ?= .venv

.PHONY: install init-db dev dev-graphical dev-text test generate-icons

install:
	$(PYTHON) -m venv $(VENV)
	$(VENV)/bin/pip install --upgrade pip wheel
	$(VENV)/bin/pip install -r server/requirements.txt

init-db:
	$(VENV)/bin/python server/manage.py init-db

dev:
	$(VENV)/bin/python server/manage.py run-dev

dev-graphical:
	EMMIE_SHELL=graphical $(VENV)/bin/python server/manage.py run-dev --shell graphical

dev-text:
	EMMIE_SHELL=text $(VENV)/bin/python server/manage.py run-dev --shell text

test:
	$(VENV)/bin/python -m unittest discover -s tests -v

generate-icons:
	$(PYTHON) scripts/generate_icons.py
