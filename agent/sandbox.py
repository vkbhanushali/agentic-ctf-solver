import subprocess
import shlex
import os
import json
from pathlib import Path

class LocalSandbox:
    """DEV ONLY. Runs commands in a subprocess scoped to the workspace dir.
    Does NOT provide network isolation. Replace with DockerSandbox for scored runs."""
    isolated = False

    def __init__(self, workspace_dir, timeout=60, max_output=8000):
        self.workspace = Path(workspace_dir).resolve()
        self.workspace.mkdir(parents=True, exist_ok=True)
        self.timeout = timeout
        self.max_output = max_output

    def exec(self, command):
        """Returns dict: stdout, stderr, exit_code, timed_out, truncated."""
        try:
            p = subprocess.run(
                ["bash", "-lc", command],
                cwd=str(self.workspace),
                capture_output=True, text=True,
                timeout=self.timeout,
                env={"PATH": os.environ.get("PATH", ""), "HOME": str(self.workspace)},
            )
            out, err, code, to = p.stdout, p.stderr, p.returncode, False
        except subprocess.TimeoutExpired as e:
            out = e.stdout or ""
            err = (e.stderr or "") + f"\n[TIMEOUT after {self.timeout}s]"
            code, to = 124, True
        if isinstance(out, bytes): out = out.decode("utf-8", "replace")
        if isinstance(err, bytes): err = err.decode("utf-8", "replace")
        combined = out + (("\n[stderr]\n" + err) if err.strip() else "")
        truncated = len(combined) > self.max_output
        if truncated:
            h = self.max_output // 2
            combined = combined[:h] + f"\n...[TRUNCATED {len(combined)-self.max_output} chars]...\n" + combined[-h:]
        return {"output": combined, "exit_code": code,
                "timed_out": to, "truncated": truncated}

    def read_file(self, filename):
        p = (self.workspace / filename).resolve()
        if not str(p).startswith(str(self.workspace)):
            return {"error": "path escapes workspace"}
        if not p.exists():
            return {"error": f"no such file: {filename}"}
        data = p.read_bytes()[: self.max_output]
        try:
            return {"content": data.decode("utf-8")}
        except UnicodeDecodeError:
            return {"content": data.hex(), "encoding": "hex"}

    def reset(self):
        pass  # workspace is recreated fresh per attempt by the controller


class DockerSandbox:
    """Run solver commands inside an isolated Docker container."""

    isolated = True

    def __init__(
        self,
        workspace_dir,
        timeout=60,
        max_output=8000,
        image="ctf-solver:local",
        container_name=None,
        network="none",
    ):
        
        import uuid

        self.workspace = Path(workspace_dir).resolve()
        self.timeout = timeout
        self.max_output = max_output
        self.image = image
        self.network = network
        self.container = (
            container_name
            or "ctf-" + uuid.uuid4().hex[:12]
        )
        self.closed = False

        if not self.workspace.is_dir():
            raise FileNotFoundError(self.workspace)

        result = subprocess.run(
            [
                "docker", "run", "-d",
                "--name", self.container,
                "--network", self.network,
                "--read-only",
                "--user", "10001:10001",
                "--cap-drop", "ALL",
                "--security-opt", "no-new-privileges",
                "--memory", "512m",
                "--memory-swap", "512m",
                "--cpus", "1",
                "--pids-limit", "64",
                "--tmpfs",
                "/work:rw,exec,nosuid,nodev,size=64m,uid=10001,gid=10001",
                "--mount",
                (
                    f"type=bind,source={self.workspace},"
                    "target=/challenge,readonly"
                ),
                self.image,
                "sleep", "infinity",
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode != 0:
            raise RuntimeError(
                "Docker startup failed: " + result.stderr
            )

    def exec(self, command):
        if self.closed:
            return {"error": "sandbox closed"}

        try:
            result = subprocess.run(
                [
                    "docker", "exec",
                    "-w", "/challenge",
                    self.container,
                    "timeout", "-k", "1",
                    str(self.timeout),
                    "bash", "-lc", command,
                ],
                capture_output=True,
                timeout=self.timeout + 5,
            )

            stdout = result.stdout.decode("utf-8", "replace")
            stderr = result.stderr.decode("utf-8", "replace")
            code = result.returncode
            timed_out = code in (124, 137)

        except subprocess.TimeoutExpired as error:
            stdout = (error.stdout or b"").decode(
                "utf-8", "replace"
            )
            stderr = (error.stderr or b"").decode(
                "utf-8", "replace"
            )
            code = 124
            timed_out = True

        combined = stdout

        if stderr.strip():
            combined += "\n[stderr]\n" + stderr

        truncated = len(combined) > self.max_output

        if truncated:
            half = self.max_output // 2
            combined = (
                combined[:half]
                + "\n...[TRUNCATED]...\n"
                + combined[-half:]
            )

        return {
            "output": combined,
            "exit_code": code,
            "timed_out": timed_out,
            "truncated": truncated,
        }

    def read_file(self, filename):
        if self.closed:
            return {"error": "sandbox closed"}

        script = r"""
import json
import pathlib
import sys

name = pathlib.Path(sys.argv[1])

if not name.is_absolute():
    name = pathlib.Path("/challenge") / name

p = name.resolve(strict=True)

if not (
    p.is_relative_to("/challenge")
    or p.is_relative_to("/work")
):
    raise ValueError("path outside sandbox")

if not p.is_file():
    raise ValueError("not a regular file")

with p.open("rb") as f:
    data = f.read(8193)

truncated = len(data) > 8192
data = data[:8192]

try:
    content = data.decode("utf-8")
    encoding = "utf-8"
except UnicodeDecodeError:
    content = data.hex()
    encoding = "hex"

print(json.dumps({
    "content": content,
    "encoding": encoding,
    "truncated": truncated,
}))
"""

        result = subprocess.run(
            [
                "docker", "exec",
                self.container,
                "python3", "-c", script, filename,
            ],
            capture_output=True,
            text=True,
            timeout=min(self.timeout, 15),
        )

        if result.returncode != 0:
            return {"error": result.stderr[:500]}

        return json.loads(result.stdout)

    def reset(self):
        if self.closed:
            return

        self.closed = True

        subprocess.run(
            ["docker", "rm", "-f", self.container],
            capture_output=True,
            timeout=15,
            check=False,
        )