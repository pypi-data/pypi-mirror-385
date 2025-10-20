#!/usr/bin/env bash

# Parameters
export NOVNC_PROXY_DIR="${1}"
export NOVNC_PROXY="${2}"
NOVNC_HOST="${3}"
export NOVNC_PORT="${4}"

export NOVNC_DIR="${NOVNC_PROXY_DIR}/novnc"

# Assure session uses HOME-dir as current working directory
cd "${HOME}"

# echo "DEBUG:" 1>&2
# env | grep NOVNC 1>&2

if [[ -z "${XDG_RUNTIME_DIR}" ]]; then
  export XDG_RUNTIME_DIR="${HOME}/.local/runtime"
  mkdir -p "${XDG_RUNTIME_DIR}"
  chmod 0700 "${XDG_RUNTIME_DIR}"
fi

SOCKET_PATH="${XDG_RUNTIME_DIR}/supervisor.sock"

if [ -S "$SOCKET_PATH" ]; then
  novnc-supervisorctl start all
else
  novnc-supervisord -n
  # -c "${NOVNC_PROXY_DIR}/extras/supervisor/supervisor.conf"
fi

# Start VNC server (tigerVNC)
# "${NOVNC_DIR}/start-vnc-server.sh"

# Start Websockify webserver serving novnc.html
# "${NOVNC_PROXY}" --listen "${NOVNC_PORT}" --web "${NOVNC_DIR}" --vnc 127.0.0.1:5900
