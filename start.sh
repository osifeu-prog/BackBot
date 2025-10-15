# start.sh (תיקון קטן)
#!/usr/bin/env bash
set -euo pipefail

PORT="${PORT:-8000}"   # <- הוסף שורה זו

python -X utf8 -m app.db
exec uvicorn server:app --host 0.0.0.0 --port "$PORT"   # <- השתמש ב-$PORT
