import os
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

# Use Render DATABASE_URL if provided, else fallback to local db
db_url = os.environ.get("DATABASE_URL", "sqlite:///db.sqlite")
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

# SQLite engine requires specific arguments
if db_url.startswith("sqlite"):
    engine = create_engine(db_url, connect_args={"check_same_thread": False})
else:
    engine = create_engine(db_url)

session = sessionmaker(autocommit=False, autoflush=False, bind=engine)