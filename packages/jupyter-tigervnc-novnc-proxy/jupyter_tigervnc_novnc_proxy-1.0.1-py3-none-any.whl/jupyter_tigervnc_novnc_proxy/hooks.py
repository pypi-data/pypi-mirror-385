import logging
import os
import subprocess
import sys
import socket
import time
import jupyter_tigervnc_novnc_proxy

logging.basicConfig(
    stream=sys.stderr,
    level="INFO",  # logging.ERROR)
)
log = logging.getLogger(__name__)
log.setLevel("INFO")


def wait_for_vnc_port():
    """
    Wait for TigerVNC service to start on port 5900 (env: VNC_PORT).

    Command: novnc-wait
    """
    try:
        port = int(os.getenv('VNC_PORT', 5900))
    except Exception as e:
        log.warning(f"[VNC] Invalid value set for VNC_PORT: '{os.getenv('VNC_PORT')}'. Defaulting to port 5900.")
        port = 5900
    if not wait_for_service('127.0.0.1', port, timeout=60):
        sys.exit(1)


def supervisorctl():
    """
    Relay supervisorctl commands to supervisorctl and pass path to novnc configs.

    Command: novnc-supervisorctl --help
    """
    if 'SUPERVISOR_RUNTIME_DIR' not in os.environ:
        os.environ['SUPERVISOR_RUNTIME_DIR'] = 'tmp'  # os.path.join(os.getenv('HOME'), '.local', 'runtime')
    runtime_dir = os.environ['SUPERVISOR_RUNTIME_DIR']

    if os.path.exists(os.path.join(runtime_dir, "supervisor.sock")):
        novnc_proxy_dir = os.path.dirname(jupyter_tigervnc_novnc_proxy.__file__)
        supervisor_conf = os.path.join(novnc_proxy_dir, "extras", "supervisor", "supervisor.conf")
        try:
            args = sys.argv[1:]
        except Exception as e:
            log.exception(e)
            log.warning("Error while fetching arguments for novnc-supervisorctl.")
            args = []
        subprocess.run(["supervisorctl", "-c", supervisor_conf] + args)
    else:
        log.error("[NOVNC] No supervisor instance running.")
        sys.exit(1)


def supervisord():
    """
    Relay supervisord commands to supervisord and pass path to novnc configs.

    Command: novnc-supervisord --help
    """
    if 'SUPERVISOR_RUNTIME_DIR' not in os.environ:
        os.environ['SUPERVISOR_RUNTIME_DIR'] = 'tmp'  # os.path.join(os.getenv('HOME'), '.local', 'runtime')
    runtime_dir = os.environ['SUPERVISOR_RUNTIME_DIR']

    if os.path.exists(runtime_dir):
        novnc_proxy_dir = os.path.dirname(jupyter_tigervnc_novnc_proxy.__file__)
        supervisor_conf = os.path.join(novnc_proxy_dir, "extras", "supervisor", "supervisor.conf")
        try:
            args = sys.argv[1:]
        except Exception as e:
            log.exception(e)
            log.warning("Error while fetching arguments for novnc-supervisord.")
            args = []
        subprocess.run(["supervisord", "-c", supervisor_conf] + args)
    else:
        log.error(f"[NOVNC] SUPERVISOR_RUNTIME_DIR={runtime_dir} does not exist.")
        sys.exit(1)


def wait_for_service(host, port, timeout=60):
    """
    Wait for a TCP service to become available.

    Args:
        host: Hostname or IP address
        port: TCP port number
        timeout: Maximum time to wait in seconds (default: 60)

    Returns:
        True if service becomes available, False if timeout occurs
    """
    time_elapsed = 0
    start_time = time.time()

    while (time_elapsed := int(time.time() - start_time)) < timeout:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((host, port))
            sock.close()

            if result == 0:
                # log.info(f"[VNC] Service on {host}:{port} is active!")
                return True
            else:
                if time_elapsed > 5:
                    log.warning(f"[VNC] Waiting for {host}:{port}... ({time_elapsed}s elapsed)")

        except socket.error as e:
            log.error(f"[VNC] Connection error: {e}")

        time.sleep(1)

    log.error(f"[VNC] Timeout: Service on {host}:{port} did not become active within {timeout} seconds")
    return False
