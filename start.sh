#!/usr/bin/env bash
set -euo pipefail
python -X utf8 -m app.db
exec uvicorn server:app --host 0.0.0.0 --port 8000
