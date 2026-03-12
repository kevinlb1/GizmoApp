#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_HELPER="${ROOT_DIR}/scripts/envfile.py"
SYNC_DEPLOY_ENV="${ROOT_DIR}/scripts/sync_deploy_env.sh"
cd "${ROOT_DIR}"

ensure_user_systemd_env() {
  if [[ -z "${XDG_RUNTIME_DIR:-}" ]]; then
    export XDG_RUNTIME_DIR="/run/user/$(id -u)"
  fi

  if [[ -z "${DBUS_SESSION_BUS_ADDRESS:-}" && -S "${XDG_RUNTIME_DIR}/bus" ]]; then
    export DBUS_SESSION_BUS_ADDRESS="unix:path=${XDG_RUNTIME_DIR}/bus"
  fi
}

if [[ -f "${ENV_HELPER}" && -f "${ROOT_DIR}/.env" ]]; then
  while IFS= read -r -d '' env_entry; do
    export "${env_entry}"
  done < <(python3 "${ENV_HELPER}" load "${ROOT_DIR}/.env")
fi

BRANCH="${GIZMOAPP_DEPLOY_BRANCH:-main}"
PYTHON_BIN="${ROOT_DIR}/.venv/bin/python"
PIP_BIN="${ROOT_DIR}/.venv/bin/pip"
CURRENT_HEAD="$(git rev-parse HEAD)"

mkdir -p "${ROOT_DIR}/var/log" "${ROOT_DIR}/var/data"

if [[ -n "$(git status --porcelain --untracked-files=no)" ]]; then
  echo "Tracked files are dirty. Refusing to deploy over local changes."
  exit 1
fi

if [[ ! -x "${PYTHON_BIN}" ]]; then
  echo "Virtualenv is missing. Run ./scripts/install_checkout.sh or ./scripts/install_server.sh first."
  exit 1
fi

git fetch origin "${BRANCH}"

read -r LOCAL_AHEAD REMOTE_AHEAD <<<"$(git rev-list --left-right --count HEAD...origin/${BRANCH})"
if (( LOCAL_AHEAD > 0 && REMOTE_AHEAD > 0 )); then
  echo "Local branch has diverged from origin/${BRANCH}. Manual intervention required."
  exit 1
fi

if (( LOCAL_AHEAD > 0 )); then
  echo "Local checkout is ahead of origin/${BRANCH}. Refusing to overwrite local commits."
  exit 1
fi

if (( REMOTE_AHEAD == 0 )); then
  echo "Already up to date."
  exit 0
fi

git merge --ff-only "origin/${BRANCH}"
CHANGED_FILES="$(git diff --name-only "${CURRENT_HEAD}" HEAD)"
env_changed=0

if [[ -x "${SYNC_DEPLOY_ENV}" ]]; then
  if "${SYNC_DEPLOY_ENV}"; then
    :
  else
    sync_status="$?"
    if [[ "${sync_status}" -eq 10 ]]; then
      env_changed=1
    else
      exit "${sync_status}"
    fi
  fi
fi

if grep -Eq '^server/requirements\.txt$' <<<"${CHANGED_FILES}"; then
  "${PIP_BIN}" install --upgrade pip wheel
  "${PIP_BIN}" install -r "${ROOT_DIR}/server/requirements.txt"
fi

"${PYTHON_BIN}" "${ROOT_DIR}/server/manage.py" init-db

needs_reload=0
while IFS= read -r path; do
  [[ -z "${path}" ]] && continue
  case "${path}" in
    AGENTS.md|README.md|.gitignore|.env.example|deploy/user-crontab.example|deploy/nginx-location.example.conf|server/gizmoapp_server/static/*)
      ;;
    *)
      needs_reload=1
      break
      ;;
  esac
done <<<"${CHANGED_FILES}"

if (( needs_reload == 0 && env_changed == 0 )); then
  echo "Deployed static or documentation changes. gunicorn reload not required."
  exit 0
fi

if [[ -n "${GIZMOAPP_SYSTEMD_USER_SERVICE:-}" ]] && command -v systemctl >/dev/null 2>&1; then
  ensure_user_systemd_env

  if (( env_changed != 0 )); then
    if systemctl --user restart "${GIZMOAPP_SYSTEMD_USER_SERVICE}"; then
      echo "Restarted ${GIZMOAPP_SYSTEMD_USER_SERVICE} after applying deploy/app.env."
      exit 0
    fi

    echo "Failed to restart ${GIZMOAPP_SYSTEMD_USER_SERVICE} via systemctl --user." >&2
    echo "Check XDG_RUNTIME_DIR and DBUS_SESSION_BUS_ADDRESS for cron-driven deploys." >&2
  fi

  if systemctl --user reload "${GIZMOAPP_SYSTEMD_USER_SERVICE}"; then
    echo "Reloaded ${GIZMOAPP_SYSTEMD_USER_SERVICE}."
    exit 0
  fi

  if systemctl --user restart "${GIZMOAPP_SYSTEMD_USER_SERVICE}"; then
    echo "Restarted ${GIZMOAPP_SYSTEMD_USER_SERVICE}."
    exit 0
  fi

  echo "Failed to reload or restart ${GIZMOAPP_SYSTEMD_USER_SERVICE} via systemctl --user." >&2
  echo "Check XDG_RUNTIME_DIR and DBUS_SESSION_BUS_ADDRESS for cron-driven deploys." >&2
fi

if [[ -n "${GIZMOAPP_GUNICORN_PID_FILE:-}" ]] && [[ -f "${GIZMOAPP_GUNICORN_PID_FILE}" ]]; then
  kill -HUP "$(cat "${GIZMOAPP_GUNICORN_PID_FILE}")"
  echo "Reloaded gunicorn via PID file."
  exit 0
fi

echo "Deploy completed, but no gunicorn reload strategy is configured."
echo "Set GIZMOAPP_SYSTEMD_USER_SERVICE or GIZMOAPP_GUNICORN_PID_FILE in .env."
exit 1
