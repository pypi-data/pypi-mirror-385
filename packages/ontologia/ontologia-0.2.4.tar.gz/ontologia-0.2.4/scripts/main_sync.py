"""
Runner do OntologySyncService

Uso:
  python scripts/main_sync.py

Config:
  - KUZU_DB_PATH: caminho do banco Kùzu (default: instance_graph.kuzu)
  - DUCKDB_PATH: caminho do banco DuckDB (opcional)
"""

from __future__ import annotations

import logging
import os
from pathlib import Path

from sqlmodel import Session, SQLModel

from api.core.database import engine
from datacatalog.models import Dataset, DatasetBranch, DatasetTransaction  # noqa: F401
from ontologia.application.sync_service import OntologySyncService
from ontologia.config import load_config
from ontologia.domain.metamodels.instances.object_type_data_source import (  # noqa: F401
    ObjectTypeDataSource,
)
from ontologia.domain.metamodels.types.link_type import LinkType  # noqa: F401

# Ensure model modules are imported so SQLModel.metadata includes all tables
from ontologia.domain.metamodels.types.object_type import ObjectType  # noqa: F401

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def run_sync(
    *,
    duckdb_path: str | None = None,
    meta_session: Session | None = None,
    kuzu_conn=None,
    duckdb_conn=None,
):
    """
    Executa o processo de sincronização. Aceita dependências injetadas para facilitar testes.
    Quando conexões não são fornecidas, tenta criá-las dinamicamente (se libs estiverem disponíveis).
    """
    config = load_config(Path(os.getenv("ONTOLOGIA_CONFIG_ROOT", Path.cwd())))
    if duckdb_conn is None and duckdb_path is None:
        duckdb_path = config.data.duckdb_path

    # Initialize the metamodel tables when running standalone (outside API lifespan)
    try:
        logger.info("Inicializando tabelas do metamodelo (runner autônomo)...")
        SQLModel.metadata.create_all(engine)
    except Exception as e:
        logger.warning(f"Falha ao inicializar tabelas do metamodelo: {e}")
    close_session = False
    if meta_session is None:
        meta_session = Session(engine)
        close_session = True

    # Criar conexão Kùzu se não fornecida
    if kuzu_conn is None:
        try:
            import kuzu  # type: ignore

            kuzu_db_path = os.getenv("KUZU_DB_PATH", config.data.kuzu_path)
            db = kuzu.Database(database_path=kuzu_db_path)
            kuzu_conn = kuzu.Connection(db)
            logger.info("KùzuDB conectado: %s", kuzu_db_path)
        except ImportError:
            logger.warning(
                "KùzuDB não instalado; executando apenas etapas que não dependem do grafo."
            )
            kuzu_conn = None

    # Criar conexão DuckDB se não fornecida e houver caminho
    if duckdb_conn is None and duckdb_path:
        try:
            import duckdb  # type: ignore

            duckdb_conn = duckdb.connect(database=duckdb_path)
            logger.info("DuckDB conectado: %s", duckdb_path)
        except ImportError:
            logger.warning("DuckDB não instalado; etapas dependentes serão ignoradas.")
            duckdb_conn = None

    try:
        svc = OntologySyncService(meta_session, kuzu_conn=kuzu_conn, duckdb_conn=duckdb_conn)
        svc.sync_ontology(duckdb_path=duckdb_path)
    finally:
        if close_session:
            meta_session.close()


if __name__ == "__main__":
    cfg = load_config(Path(os.getenv("ONTOLOGIA_CONFIG_ROOT", Path.cwd())))
    run_sync(
        duckdb_path=os.getenv("DUCKDB_PATH", cfg.data.duckdb_path),
    )
