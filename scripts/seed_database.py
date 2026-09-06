import os
from pathlib import Path

from sqlalchemy import create_engine, text

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg://postgres:postgres@localhost:5432/sentinelaidb")
engine = create_engine(DATABASE_URL)

schema_path = Path(__file__).resolve().parents[1] / "database" / "schema.sql"

with engine.begin() as conn:
    conn.execute(text(schema_path.read_text()))

print("Database schema initialized")
