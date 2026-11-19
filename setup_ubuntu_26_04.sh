#!/usr/bin/env bash
set -euo pipefail

# Configuration: system tools for this repository on Ubuntu 26.04 Desktop.
# Python libraries are installed from the pinned requirements.txt below.
APT_PACKAGES=(
    build-essential
    git
    htop
    openssh-client
    python3-tk
    python3-venv
    rsync
    tmux
)

REPO_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
VENV="$REPO_ROOT/.venv"

if (( EUID == 0 )); then
    printf 'Run this script as your normal user; it will request sudo for apt.\n' >&2
    exit 1
fi

if [[ ! -r /etc/os-release ]]; then
    printf 'Cannot identify the operating system.\n' >&2
    exit 1
fi

# shellcheck disable=SC1091
source /etc/os-release
if [[ "${ID:-}" != ubuntu || "${VERSION_ID:-}" != 26.04 ]]; then
    printf 'This script is intended for Ubuntu 26.04; found %s %s.\n' \
        "${ID:-unknown}" "${VERSION_ID:-unknown}" >&2
    exit 1
fi

sudo apt-get update
sudo apt-get upgrade -y
sudo apt-get install -y "${APT_PACKAGES[@]}"

if [[ ! -e "$VENV" ]]; then
    python3 -m venv "$VENV"
fi
if [[ ! -x "$VENV/bin/python" ]]; then
    printf 'The existing .venv is unusable. Move it aside and rerun this script.\n' >&2
    exit 1
fi

"$VENV/bin/python" -m pip install --upgrade pip
"$VENV/bin/python" -m pip install -r "$REPO_ROOT/requirements.txt"
"$VENV/bin/python" -m pip check
"$VENV/bin/python" -c 'import tkinter, matplotlib, nltk, numpy, scipy; print("Python packages imported successfully")'

printf '\nSetup complete. Use %s/bin/python to run this project.\n' "$VENV"
