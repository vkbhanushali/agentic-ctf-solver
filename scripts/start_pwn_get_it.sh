#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
CHALLENGE_DIR="$PROJECT_ROOT/../../external/CTFTiny/ctftiny/pwn/get_it?"

NETWORK="ctf-pwn-test"
CONTAINER="ctf-get-it-service"

# Check original CTFTiny challenge files
if [ ! -f "$CHALLENGE_DIR/Dockerfile" ]; then
    echo "ERROR: Original CTFTiny challenge files not found."
    exit 1
fi

# Create private network if missing
docker network inspect "$NETWORK" >/dev/null 2>&1 || \
    docker network create --internal "$NETWORK"

# Build original challenge service
docker build \
    -t ctf-get-it:local \
    "$CHALLENGE_DIR"

# Remove previous service container if present
docker rm -f "$CONTAINER" >/dev/null 2>&1 || true

# Start the vulnerable service
docker run -d \
    --name "$CONTAINER" \
    --network "$NETWORK" \
    --network-alias pwn.chal.csaw.io \
    --cap-drop ALL \
    --cap-add SETUID \
    --cap-add SETGID \
    --security-opt no-new-privileges \
    --memory 256m \
    --pids-limit 64 \
    ctf-get-it:local

echo "PASS: pwn-get-it service started"
echo "Network: $NETWORK"
echo "Service: $CONTAINER:1437"
