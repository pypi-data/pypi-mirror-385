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

# if [[ -z "${XDG_RUNTIME_DIR}" ]]; then
#   export XDG_RUNTIME_DIR="${HOME}/.local/runtime"
#   mkdir -p "${XDG_RUNTIME_DIR}"
#   chmod 0700 "${XDG_RUNTIME_DIR}"
# fi

# SOCKET_PATH="${XDG_RUNTIME_DIR}/supervisor.sock"
SOCKET_PATH="${SUPERVISOR_RUNTIME_DIR}/supervisor.sock"

# Proxy signals
function kill_app(){
    # correct forwarding of shutdown signal
    _wait_pid=$!
    kill -s SIGTERM $_wait_pid
    trap - SIGTERM && kill -- -$$
    if [ -n "$(pidof xinit)" ] ; then
        ### ignore the errors if not alive any more
        kill $(pidof xinit) > /dev/null 2>&1
    fi
    exit 0 # exit okay
}
trap "kill_app" SIGINT SIGTERM SIGQUIT EXIT


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
