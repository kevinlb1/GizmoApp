PYTHON ?= python3
VENV ?= .venv

.PHONY: install init-db dev dev-auto dev-graphical dev-text test validate visual-install visual-check generate-icons

install:
	$(PYTHON) -m venv $(VENV)
	$(VENV)/bin/pip install --upgrade pip wheel
	$(VENV)/bin/pip install -r server/requirements.txt

init-db:
	$(VENV)/bin/python server/manage.py init-db

dev:
	$(VENV)/bin/python server/manage.py run-dev

dev-auto:
	GIZMOAPP_SHELL=auto $(VENV)/bin/python server/manage.py run-dev --shell auto

dev-graphical:
	GIZMOAPP_SHELL=graphical $(VENV)/bin/python server/manage.py run-dev --shell graphical

dev-text:
	GIZMOAPP_SHELL=text $(VENV)/bin/python server/manage.py run-dev --shell text

test:
	$(VENV)/bin/python -m unittest discover -s tests -v

validate:
	./scripts/run_local_validation.sh

visual-install:
	@if [ -x "$(VENV)/bin/python" ]; then PYBIN="$(VENV)/bin/python"; else PYBIN="$(PYTHON)"; fi; \
		$$PYBIN -m pip install -r server/requirements-visual.txt; \
		$$PYBIN -m playwright install chromium

visual-check:
	@if [ -x "$(VENV)/bin/python" ]; then PYBIN="$(VENV)/bin/python"; else PYBIN="$(PYTHON)"; fi; \
		$$PYBIN scripts/visual_verify.py

generate-icons:
	$(PYTHON) scripts/generate_icons.py
