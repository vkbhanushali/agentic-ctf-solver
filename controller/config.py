import os

CONFIG_ID = "claude-haiku-docker-v2"

MODEL = os.environ.get("DUKE_MODEL", "claude-haiku-5-5")

BASE_URL = os.environ.get(
    "DUKE_BASE_URL",
    "https://litellm.oit.duke.edu/v1",
).rstrip("/")

MAX_STEPS = 40
MAX_WALL_SECONDS = 20 * 60
MAX_TOTAL_TOKENS = 600_000
MAX_OUTPUT_TOKENS = 4096

TOOL_TIMEOUT_SECONDS = 60
MAX_TOOL_OUTPUT_CHARS = 8000

SOLVER_IMAGE = "ctf-solver:local"
SOLVER_PLATFORM = "linux/amd64"

PRICE_IN_PER_MTOK = 0.10
PRICE_OUT_PER_MTOK = 0.50


def snapshot():
    return {
        key: value
        for key, value in globals().items()
        if key.isupper()
    }