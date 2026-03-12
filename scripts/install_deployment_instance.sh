#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  ./scripts/install_deployment_instance.sh --name NAME --repo-url URL [options]

Creates or updates a deployable checkout for one app instance under
  /home/kevinlb/bin/NAME
then installs the Python environment, writes a user-level gunicorn service,
installs a cron entry, and generates an nginx location snippet.

Options:
  --name NAME            URL path and checkout directory name, e.g. "todoapp"
  --repo-url URL         Git URL for the fork/template-derived repository
  --branch BRANCH        Git branch to deploy (default: main)
  --shell SHELL          graphical or text fallback when deploy/app.env does not set GIZMOAPP_SHELL (default: graphical)
  --app-title TITLE      Human-readable app title (default: NAME)
  --base-dir DIR         Parent directory for deployments (default: /home/kevinlb/bin)
  --domain DOMAIN        Public host name (default: vickrey10.cs.ubc.ca)
  --port PORT            Local gunicorn port; auto-selected if omitted
  --nginx-managed-dir    nginx include directory used by the one-time router bootstrap
                         (default: /etc/nginx/gizmoapp-instances)
  --skip-nginx-register  Do not copy the generated snippet into the managed nginx dir
  --skip-cron            Do not install/update the user crontab entry
  --skip-service-start   Write the user service file but do not enable/start it
  -h, --help             Show this help
EOF
}

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_HELPER="${SCRIPT_DIR}/envfile.py"

set_env_value() {
  local file="$1"
  local key="$2"
  local value="$3"

  python3 "${ENV_HELPER}" set "${file}" "${key}" "${value}"
}

get_env_value() {
  local file="$1"
  local key="$2"

  python3 "${ENV_HELPER}" get "${file}" "${key}"
}

port_is_reserved() {
  local port="$1"

  if command -v ss >/dev/null 2>&1; then
    if ss -ltnH 2>/dev/null | awk '{print $4}' | grep -Eq "[:.]${port}$"; then
      return 0
    fi
  fi

  if [[ -d "${BASE_DIR}" ]]; then
    local env_file
    while IFS= read -r -d '' env_file; do
      if [[ "$(get_env_value "${env_file}" GIZMOAPP_PORT)" == "${port}" ]]; then
        return 0
      fi
    done < <(find "${BASE_DIR}" -mindepth 2 -maxdepth 2 -name .env -type f -print0 2>/dev/null)
  fi

  return 1
}

pick_port() {
  if [[ -n "${PORT}" ]]; then
    echo "${PORT}"
    return 0
  fi

  local candidate
  for candidate in $(seq 8100 8999); do
    if ! port_is_reserved "${candidate}"; then
      echo "${candidate}"
      return 0
    fi
  done

  echo "Could not find a free local gunicorn port in the range 8100-8999." >&2
  exit 1
}

install_cron_entry() {
  local cron_line="$1"
  local tmp_crontab

  if ! command -v crontab >/dev/null 2>&1; then
    echo "crontab is not available; skipping cron installation."
    return 0
  fi

  tmp_crontab="$(mktemp)"
  crontab -l 2>/dev/null > "${tmp_crontab}" || true
  if grep -Fqx "${cron_line}" "${tmp_crontab}"; then
    echo "Cron entry already present."
  else
    printf '%s\n' "${cron_line}" >> "${tmp_crontab}"
    crontab "${tmp_crontab}"
    echo "Installed cron entry."
  fi
  rm -f "${tmp_crontab}"
}

register_nginx_instance() {
  local source_snippet="$1"
  local target_snippet="${NGINX_MANAGED_DIR}/${NAME}.conf"

  if (( SKIP_NGINX_REGISTER != 0 )); then
    echo "Automatic nginx registration skipped."
    return 0
  fi

  if [[ ! -d "${NGINX_MANAGED_DIR}" ]]; then
    echo "Managed nginx dir ${NGINX_MANAGED_DIR} does not exist; skipping automatic nginx registration."
    echo "Run ./scripts/install_nginx_instance_router.sh once on the server to enable single-command app installs."
    return 0
  fi

  if ! command -v sudo >/dev/null 2>&1 || ! command -v nginx >/dev/null 2>&1; then
    echo "sudo and nginx are required for automatic nginx registration; skipping."
    return 0
  fi

  sudo install -d -m 755 "${NGINX_MANAGED_DIR}"
  sudo install -m 644 "${source_snippet}" "${target_snippet}"
  sudo nginx -t
  sudo systemctl reload nginx
  echo "Registered nginx route in ${target_snippet} and reloaded nginx."
}

NAME=""
REPO_URL=""
BRANCH="main"
SHELL_VARIANT="graphical"
APP_TITLE=""
BASE_DIR="/home/kevinlb/bin"
DOMAIN="vickrey10.cs.ubc.ca"
PORT=""
NGINX_MANAGED_DIR="/etc/nginx/gizmoapp-instances"
SKIP_CRON=0
SKIP_NGINX_REGISTER=0
SKIP_SERVICE_START=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --name)
      NAME="$2"
      shift 2
      ;;
    --repo-url)
      REPO_URL="$2"
      shift 2
      ;;
    --branch)
      BRANCH="$2"
      shift 2
      ;;
    --shell)
      SHELL_VARIANT="$2"
      shift 2
      ;;
    --app-title)
      APP_TITLE="$2"
      shift 2
      ;;
    --base-dir)
      BASE_DIR="$2"
      shift 2
      ;;
    --domain)
      DOMAIN="$2"
      shift 2
      ;;
    --port)
      PORT="$2"
      shift 2
      ;;
    --nginx-managed-dir)
      NGINX_MANAGED_DIR="$2"
      shift 2
      ;;
    --skip-nginx-register)
      SKIP_NGINX_REGISTER=1
      shift
      ;;
    --skip-cron)
      SKIP_CRON=1
      shift
      ;;
    --skip-service-start)
      SKIP_SERVICE_START=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage
      exit 1
      ;;
  esac
done

if [[ -z "${NAME}" || -z "${REPO_URL}" ]]; then
  usage
  exit 1
fi

if [[ ! "${NAME}" =~ ^[A-Za-z0-9_-]+$ ]]; then
  echo "--name must contain only letters, digits, hyphens, or underscores." >&2
  exit 1
fi

case "${SHELL_VARIANT}" in
  graphical|text)
    ;;
  *)
    echo "--shell must be graphical or text." >&2
    exit 1
    ;;
esac

if [[ -z "${APP_TITLE}" ]]; then
  APP_TITLE="${NAME}"
fi

APP_DIR="${BASE_DIR}/${NAME}"
URL_PREFIX="/${NAME}"
SERVICE_NAME="${NAME}.service"
USER_SYSTEMD_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/systemd/user"
SERVICE_FILE="${USER_SYSTEMD_DIR}/${SERVICE_NAME}"
GENERATED_DIR="${APP_DIR}/var/generated"
NGINX_SNIPPET="${GENERATED_DIR}/nginx-location.conf"
USER_RUNTIME_DIR="/run/user/$(id -u)"

if ! command -v git >/dev/null 2>&1 || ! command -v python3 >/dev/null 2>&1; then
  echo "git and python3 are required. Run ./scripts/install_machine_dependencies.sh first." >&2
  exit 1
fi

if [[ ! -f "${ENV_HELPER}" ]]; then
  echo "Missing ${ENV_HELPER}" >&2
  exit 1
fi

mkdir -p "${BASE_DIR}"

if [[ -d "${APP_DIR}/.git" ]]; then
  git -C "${APP_DIR}" remote set-url origin "${REPO_URL}"
else
  if [[ -e "${APP_DIR}" ]] && [[ -n "$(find "${APP_DIR}" -mindepth 1 -maxdepth 1 2>/dev/null)" ]]; then
    echo "${APP_DIR} exists and is not an empty git checkout. Refusing to overwrite it." >&2
    exit 1
  fi
  rm -rf "${APP_DIR}"
  git clone "${REPO_URL}" "${APP_DIR}"
fi

git -C "${APP_DIR}" fetch origin "${BRANCH}"
git -C "${APP_DIR}" checkout -B "${BRANCH}" "origin/${BRANCH}"

if [[ ! -x "${APP_DIR}/scripts/install_checkout.sh" ]]; then
  echo "The repository at ${REPO_URL} does not contain scripts/install_checkout.sh." >&2
  echo "It may be based on an older scaffold." >&2
  exit 1
fi

if [[ ! -f "${APP_DIR}/.env" ]]; then
  cp "${APP_DIR}/.env.example" "${APP_DIR}/.env"
fi
chmod 600 "${APP_DIR}/.env"

PORT="$(pick_port)"
tracked_shell=""
if [[ -f "${APP_DIR}/deploy/app.env" ]]; then
  tracked_shell="$(get_env_value "${APP_DIR}/deploy/app.env" GIZMOAPP_SHELL)"
fi
effective_shell="${tracked_shell:-${SHELL_VARIANT}}"

set_env_value "${APP_DIR}/.env" GIZMOAPP_APP_NAME "${APP_TITLE}"
set_env_value "${APP_DIR}/.env" GIZMOAPP_SHELL "${effective_shell}"
set_env_value "${APP_DIR}/.env" GIZMOAPP_URL_PREFIX "${URL_PREFIX}"
set_env_value "${APP_DIR}/.env" GIZMOAPP_DB_PATH "${APP_DIR}/var/data/${NAME}.sqlite3"
set_env_value "${APP_DIR}/.env" GIZMOAPP_PORT "${PORT}"
set_env_value "${APP_DIR}/.env" GIZMOAPP_DEPLOY_BRANCH "${BRANCH}"
set_env_value "${APP_DIR}/.env" GIZMOAPP_SYSTEMD_USER_SERVICE "${SERVICE_NAME}"

current_secret="$(get_env_value "${APP_DIR}/.env" GIZMOAPP_SECRET_KEY)"
if [[ -z "${current_secret}" || "${current_secret}" == "change-me-before-production" || "${current_secret}" == "dev-only-secret" ]]; then
  set_env_value "${APP_DIR}/.env" GIZMOAPP_SECRET_KEY "$(python3 -c 'import secrets; print(secrets.token_hex(32))')"
fi
chmod 600 "${APP_DIR}/.env"

"${APP_DIR}/scripts/install_checkout.sh"

mkdir -p "${USER_SYSTEMD_DIR}" "${GENERATED_DIR}"
cat > "${SERVICE_FILE}" <<EOF
[Unit]
Description=${APP_TITLE} gunicorn service
After=network.target

[Service]
Type=simple
WorkingDirectory=${APP_DIR}
EnvironmentFile=${APP_DIR}/.env
ExecStart=${APP_DIR}/.venv/bin/gunicorn --config ${APP_DIR}/deploy/gunicorn.conf.py server.wsgi:app
ExecReload=/bin/kill -HUP \$MAINPID
Restart=on-failure
RestartSec=3
PrivateTmp=true

[Install]
WantedBy=default.target
EOF

cat > "${NGINX_SNIPPET}" <<EOF
# Generated by scripts/install_deployment_instance.sh for ${APP_TITLE}
location = ${URL_PREFIX} {
    return 302 ${URL_PREFIX}/;
}

location ${URL_PREFIX}/ {
    proxy_pass http://127.0.0.1:${PORT};
    proxy_http_version 1.1;
    proxy_set_header Host \$host;
    proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto \$scheme;
    proxy_set_header X-Forwarded-Prefix ${URL_PREFIX};
}
EOF

register_nginx_instance "${NGINX_SNIPPET}"

if command -v systemctl >/dev/null 2>&1; then
  if systemctl --user daemon-reload; then
    if (( SKIP_SERVICE_START == 0 )); then
      if systemctl --user enable --now "${SERVICE_NAME}"; then
        echo "Enabled and started user service ${SERVICE_NAME}."
      else
        echo "Wrote ${SERVICE_FILE}, but could not enable/start it automatically."
      fi
    else
      echo "Wrote ${SERVICE_FILE}. Service start was skipped."
    fi
  else
    echo "Wrote ${SERVICE_FILE}, but systemctl --user is not ready in this session."
  fi
else
  echo "Wrote ${SERVICE_FILE}, but systemctl is not available on this machine."
fi

if command -v loginctl >/dev/null 2>&1; then
  if [[ "$(loginctl show-user "${USER}" --property=Linger --value 2>/dev/null || true)" != "yes" ]]; then
    echo "Note: user-level services may not survive logout until linger is enabled."
    echo "      A privileged user can run: sudo loginctl enable-linger ${USER}"
  fi
fi

CRON_LINE="* * * * * cd ${APP_DIR} && XDG_RUNTIME_DIR=${USER_RUNTIME_DIR} DBUS_SESSION_BUS_ADDRESS=unix:path=${USER_RUNTIME_DIR}/bus ${APP_DIR}/scripts/deploy_from_git.sh >> ${APP_DIR}/var/log/deploy-cron.log 2>&1"
if (( SKIP_CRON == 0 )); then
  install_cron_entry "${CRON_LINE}"
else
  echo "Cron installation skipped."
fi

echo
echo "Deployment instance is ready:"
echo "  App title: ${APP_TITLE}"
echo "  Repo checkout: ${APP_DIR}"
echo "  Branch: ${BRANCH}"
echo "  Shell: ${effective_shell}"
if [[ -n "${tracked_shell}" ]]; then
  echo "  Shell source: deploy/app.env"
fi
echo "  URL: http://${DOMAIN}${URL_PREFIX}/"
echo "  Local gunicorn port: ${PORT}"
echo "  User service file: ${SERVICE_FILE}"
echo "  Generated nginx snippet: ${NGINX_SNIPPET}"
if (( SKIP_NGINX_REGISTER == 0 )); then
  echo "  Managed nginx dir: ${NGINX_MANAGED_DIR}"
fi
echo
echo "Next steps:"
echo "  1. Review ${APP_DIR}/.env"
if (( SKIP_NGINX_REGISTER == 0 )); then
  echo "  2. Verify the service with: systemctl --user status ${SERVICE_NAME}"
  echo "  3. Visit http://${DOMAIN}${URL_PREFIX}/"
else
  echo "  2. Add the nginx snippet to the ${DOMAIN} server config and reload nginx"
  echo "  3. Verify the service with: systemctl --user status ${SERVICE_NAME}"
  echo "  4. Visit http://${DOMAIN}${URL_PREFIX}/"
fi
