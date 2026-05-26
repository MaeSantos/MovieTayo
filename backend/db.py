from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# SQLite DB file inside backend folder, regardless of launch directory.
DB_PATH = Path(__file__).resolve().parent / "movie_app.db"
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH.as_posix()}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

