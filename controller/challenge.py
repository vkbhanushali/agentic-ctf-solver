import hashlib, json, shutil
from pathlib import Path
from nyuctf.dataset import CTFDataset
from nyuctf.challenge import CTFChallenge

# Files/dirs that must NEVER reach the solver (hold answers or server internals)
FORBIDDEN = {"challenge.json", "test_solver", "docker-compose.yml",
             "Dockerfile", ".git", "flag", "flag.txt"}

class Challenge:
    """Controller-side wrapper. Holds the flag; exposes a sanitized solver view."""
    def __init__(self, dataset_json, challenge_id):
        self.id = challenge_id
        self.ds = CTFDataset(dataset_json=dataset_json)
        self._c = CTFChallenge(self.ds.get(challenge_id), self.ds.basedir)
        self.name = self._c.name
        self.category = self._c.category
        self.description = self._c.description or ""
        self.listed_files = list(self._c.files or [])
        self._flag = self._c.flag                 # SECRET
        self.src_dir = Path(self._c.challenge_dir)

    def expected_flag(self):
        """Controller-only. Never call this from solver/agent code."""
        return self._flag

    def solver_context(self):
        """Exactly what the solver is allowed to see."""
        return {
            "challenge_id": self.id,
            "category": self.category,
            "description": self.description,
            "files": self.listed_files,
        }

    def stage_files(self, workspace_dir):
        """Stage only declared contestant files into a fresh workspace."""

        ws = Path(workspace_dir).resolve()
        ws.mkdir(parents=True, exist_ok=True)

        source_root = self.src_dir.resolve(strict=True)
        inventory = {}

        for fname in self.listed_files:
            if not isinstance(fname, str) or not fname:
                raise ValueError("Invalid contestant filename")

            relative = Path(fname)

            if (
                relative.is_absolute()
                or ".." in relative.parts
                or any(part in FORBIDDEN for part in relative.parts)
            ):
                raise ValueError(
                    f"Forbidden contestant path: {fname}"
                )

            src = source_root / relative

            if src.is_symlink():
                raise ValueError(
                    f"Symlink contestant file rejected: {fname}"
                )

            resolved = src.resolve(strict=True)

            if not resolved.is_relative_to(source_root):
                raise ValueError(
                    f"Contestant path escapes source: {fname}"
                )

            if not resolved.is_file():
                raise ValueError(
                    f"Contestant file is not regular: {fname}"
                )

            dst = ws / relative
            dst.parent.mkdir(parents=True, exist_ok=True)

            if dst.exists() or dst.is_symlink():
                raise ValueError(
                    f"Destination already exists: {fname}"
                )

            shutil.copyfile(resolved, dst)

            inventory[fname] = {
                "status": "staged",
                "sha256": hashlib.sha256(
                    resolved.read_bytes()
                ).hexdigest(),
                "bytes": resolved.stat().st_size,
            }

        return inventory
