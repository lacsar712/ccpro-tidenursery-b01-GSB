#!/bin/sh
set -e

echo "Waiting for PostgreSQL..."
python - <<'PY'
import os, time
from sqlalchemy import create_engine, text

url = os.environ["DATABASE_URL"]
for i in range(60):
    try:
        engine = create_engine(url)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("Database is ready.")
        break
    except Exception as e:
        print(f"DB not ready ({i+1}/60): {e}")
        time.sleep(2)
else:
    raise SystemExit("Database not ready after retries")
PY

echo "Creating tables..."
python -c "from app.database import Base, engine; from app import models; Base.metadata.create_all(bind=engine)"

echo "Ensuring water_samples depth/transparency columns..."
python - <<'PY'
# create_all 不会给已存在的表补列；对旧数据卷幂等加列（历史行保持 NULL 可空）。
from sqlalchemy import text
from app.database import engine

with engine.begin() as conn:
    conn.execute(text(
        "ALTER TABLE water_samples "
        "ADD COLUMN IF NOT EXISTS sampling_depth_m DOUBLE PRECISION"
    ))
    conn.execute(text(
        "ALTER TABLE water_samples "
        "ADD COLUMN IF NOT EXISTS transparency_cm INTEGER"
    ))
print("Columns ready.")
PY

echo "Seeding data..."
python -c "from app.seed import seed; seed()"

echo "Starting uvicorn..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8400
