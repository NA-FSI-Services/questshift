#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"
python3 -m ruff check tools tests
python3 -m ruff format --check tools tests
python3 -m pytest
python3 -m tools.specs
