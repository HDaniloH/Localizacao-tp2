"""Configuração da engine e sessão do banco de dados PostgreSQL/PostGIS."""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://tp2_user:tp2_password@localhost:5432/ocorrencias_db",
)

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Fornece uma sessão transacional do banco de dados para as rotas."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
