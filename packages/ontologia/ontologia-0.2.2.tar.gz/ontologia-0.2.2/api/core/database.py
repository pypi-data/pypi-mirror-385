"""
core/database.py
----------------
Configuração agnóstica de banco de dados para o metamodelo.

Suporta:
- SQLite (desenvolvimento local, sem configuração)
- PostgreSQL (produção, via DATABASE_URL)
"""

import os

from sqlalchemy.engine import Engine
from sqlmodel import Session, create_engine

# Detecta DATABASE_URL do ambiente, usa SQLite por padrão
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///metamodel.db")
print(f"INFO: Conectando ao banco de dados de metamodelo: {DATABASE_URL}")

# SQLite requer check_same_thread=False para FastAPI
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

# Engine principal - único ponto de configuração
engine: Engine = create_engine(
    DATABASE_URL, echo=False, connect_args=connect_args  # Set True para debug SQL
)


def get_session():
    """
    Dependência do FastAPI para injetar uma sessão de DB por requisição.

    Uso em endpoints:
        @app.get("/items")
        def get_items(session: Session = Depends(get_session)):
            ...
    """
    with Session(engine) as session:
        yield session
