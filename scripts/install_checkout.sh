#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: ./scripts/install_checkout.sh

Initializes the current checkout for local serving on a machine that already has
system dependencies installed. Safe to re-run.
EOF
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

if [[ ! -f "${ROOT_DIR}/.env.example" ]]; then
  echo "Missing .env.example in ${ROOT_DIR}" >&2
  exit 1
fi

if [[ ! -f "${ROOT_DIR}/.env" ]]; then
  cp "${ROOT_DIR}/.env.example" "${ROOT_DIR}/.env"
  echo "Created ${ROOT_DIR}/.env from .env.example. Review the values before starting gunicorn."
fi

set -a
# shellcheck source=/dev/null
. "${ROOT_DIR}/.env"
set +a

mkdir -p "${ROOT_DIR}/var/data" "${ROOT_DIR}/var/log"

if [[ ! -x "${ROOT_DIR}/.venv/bin/python" ]]; then
  python3 -m venv "${ROOT_DIR}/.venv"
fi

"${ROOT_DIR}/.venv/bin/pip" install --upgrade pip wheel
"${ROOT_DIR}/.venv/bin/pip" install -r "${ROOT_DIR}/server/requirements.txt"
"${ROOT_DIR}/.venv/bin/python" "${ROOT_DIR}/server/manage.py" init-db

describe_args=()
if [[ -n "${GIZMOAPP_SHELL:-}" ]]; then
  describe_args+=(--shell "${GIZMOAPP_SHELL}")
fi
"${ROOT_DIR}/.venv/bin/python" "${ROOT_DIR}/server/manage.py" describe "${describe_args[@]}"

echo
echo "Checkout install complete for ${ROOT_DIR}."
echo "Next steps:"
echo "  1. Review ${ROOT_DIR}/.env"
echo "  2. Start or reload the gunicorn user service for this checkout"
echo "  3. Ensure nginx routes traffic to the configured GIZMOAPP_URL_PREFIX and GIZMOAPP_PORT"

