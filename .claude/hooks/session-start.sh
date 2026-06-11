#!/bin/bash
set -euo pipefail

if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

# cffi must be upgraded before pymongo can import its SSL backend
pip install cffi --upgrade -q
pip install -r "$CLAUDE_PROJECT_DIR/requirements.txt" -q
