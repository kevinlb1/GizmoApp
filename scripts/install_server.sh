#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if command -v sudo >/dev/null 2>&1; then
  SUDO="sudo"
else
  SUDO=""
fi

"${SUDO}" apt-get update
"${SUDO}" apt-get install -y python3 python3-venv python3-pip sqlite3 git curl

if [[ ! -f "${ROOT_DIR}/.env" ]]; then
  cp "${ROOT_DIR}/.env.example" "${ROOT_DIR}/.env"
  echo "Created ${ROOT_DIR}/.env from .env.example. Review the values before starting gunicorn."
fi

set -a
# shellcheck source=/dev/null
. "${ROOT_DIR}/.env"
set +a

mkdir -p "${ROOT_DIR}/var/data" "${ROOT_DIR}/var/log"
python3 -m venv "${ROOT_DIR}/.venv"
"${ROOT_DIR}/.venv/bin/pip" install --upgrade pip wheel
"${ROOT_DIR}/.venv/bin/pip" install -r "${ROOT_DIR}/server/requirements.txt"
"${ROOT_DIR}/.venv/bin/python" "${ROOT_DIR}/server/manage.py" init-db
"${ROOT_DIR}/.venv/bin/python" "${ROOT_DIR}/server/manage.py" describe

echo
echo "Install complete."
echo "Next steps:"
echo "  1. Review ${ROOT_DIR}/.env"
echo "  2. Choose GIZMOAPP_SHELL=graphical or GIZMOAPP_SHELL=text in ${ROOT_DIR}/.env"
echo "  3. Install the user service from deploy/gizmoapp-gunicorn.service.example"
echo "  4. Configure nginx using deploy/nginx-location.example.conf"
echo "  5. Add the cron entry from deploy/user-crontab.example"
