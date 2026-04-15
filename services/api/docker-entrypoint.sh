#!/usr/bin/env sh

set -eu

python - << 'PY'
import os
import time

from sqlalchemy import create_engine, text

url = os.environ.get("APP_DATABASE_URL")
if not url:
    raise SystemExit("APP_DATABASE_URL is required")

engine = create_engine(url, pool_pre_ping=True)

last_err = None
for _ in range(60):
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        last_err = None
        break
    except Exception as e:
        last_err = e
        time.sleep(1)

if last_err is not None:
    raise last_err
PY

alembic -c /app/alembic.ini upgrade head

exec uvicorn app.main:app --host 0.0.0.0 --port 8000
