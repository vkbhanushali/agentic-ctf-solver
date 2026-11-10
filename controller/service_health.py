
import json
import subprocess


def check_pwn_service(
    network="ctf-pwn-test",
    host="ctf-get-it-service",
    port=1437,
    image="ctf-solver:local",
):
    """Check whether the original pwn service responds correctly."""

    script = """
import socket
import sys

host = sys.argv[1]
port = int(sys.argv[2])

try:
    with socket.create_connection((host, port), timeout=5) as sock:
        sock.settimeout(5)
        data = bytearray()

        while len(data) < 8192:
            chunk = sock.recv(4096)
            if not chunk:
                break
            data.extend(chunk)
            if b"Do you gets it??" in data:
                break

        if b"Do you gets it??" not in data:
            print("FAIL: Challenge prompt not received")
            sys.exit(1)

        print("PASS: Challenge service ready")

except Exception as exc:
    print("FAIL:", type(exc).__name__, str(exc))
    sys.exit(1)
"""

    command = [
        "docker", "run", "--rm",
        "--network", network,
        "--user", "10001:10001",
        "--cap-drop", "ALL",
        "--security-opt", "no-new-privileges",
        "--memory", "128m",
        "--pids-limit", "32",
        "--entrypoint", "python3",
        image,
        "-c", script,
        host,
        str(port),
    ]

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=20,
            check=False,
        )
    except (subprocess.TimeoutExpired, OSError) as exc:
        return {
            "ready": False,
            "reason": str(exc)[:300],
        }

    return {
        "ready": result.returncode == 0,
        "reason": (
            result.stdout.strip()
            or result.stderr.strip()
        )[:300],
    }
