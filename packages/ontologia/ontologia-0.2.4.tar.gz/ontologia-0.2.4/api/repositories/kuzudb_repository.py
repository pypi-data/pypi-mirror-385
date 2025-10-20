"""
repositories/kuzudb_repository.py
----------------------------------
Singleton para gerenciar a conexão e operações com o KuzuDB (grafo).

Responsabilidades:
- Manter conexão única com KuzuDB
- Inicializar schema do grafo (Object, LinkedObject)
- Fornecer interface para operações de grafo
"""

import os
import threading
from typing import TYPE_CHECKING, Any, Optional, cast

from ontologia.config import use_unified_graph_enabled

# Import opcional - KuzuDB pode não estar instalado
try:
    import kuzu

    KUZU_AVAILABLE = True
except ImportError:
    KUZU_AVAILABLE = False
    kuzu = None

if TYPE_CHECKING:  # pragma: no cover - only for static type checking
    pass


class KuzuDBRepository:
    """
    Singleton para gerenciar a conexão e as operações com o KuzuDB.

    Schema do Grafo:
    ----------------
    NODE TABLE Object:
        - rid: STRING (PRIMARY KEY)
        - object_type_rid: STRING (ref ao ObjectType do metamodelo)
        - primary_key_value: STRING
        - properties: STRING (JSON serializado)

    REL TABLE LinkedObject:
        - FROM Object TO Object
        - rid: STRING
        - link_type_rid: STRING (ref ao LinkType do metamodelo)
        - properties: STRING (JSON serializado)
    """

    _instance: Optional["KuzuDBRepository"] = None
    _lock = threading.Lock()

    db: Any | None = None
    conn: Any | None = None

    def __new__(cls, *args, **kwargs):
        """Implementação Singleton thread-safe."""
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, db_path: str = "instance_graph.kuzu"):
        """
        Inicializa a conexão KuzuDB (apenas uma vez, devido ao Singleton).

        Args:
            db_path: Caminho para o diretório do banco KuzuDB
        """
        # Evitar reinicialização no singleton
        if hasattr(self, "conn"):
            return

        if not KUZU_AVAILABLE:
            print("WARNING: KuzuDB não está instalado. Funcionalidades de grafo desabilitadas.")
            print("         Install com: pip install kuzu")
            self.db = None
            self.conn = None
            return

        assert kuzu is not None  # noqa: S101 - defensive guard for type checkers

        kuzu_db_path = os.getenv("KUZU_DB_PATH", db_path)
        print(f"INFO: Conectando ao banco de dados de grafo: {kuzu_db_path}")

        database = cast(Any, kuzu.Database(database_path=kuzu_db_path))
        connection = cast(Any, kuzu.Connection(database))
        self.db = database
        self.conn = connection
        # In unified graph mode, schema is managed by SyncService; skip legacy auto-init
        use_unified = use_unified_graph_enabled()
        if use_unified:
            print(
                "INFO: Unified graph mode enabled; skipping KuzuDBRepository auto schema initialization."
            )
        else:
            self._initialize_schema()

    def _initialize_schema(self):
        """
        Cria o schema para Objects e LinkedObjects se não existir.

        Este método é idempotente (pode ser chamado múltiplas vezes).
        """
        if not self.conn:
            return

        print("INFO: Inicializando/verificando schema do KuzuDB...")

        # Criar NODE TABLE para Object (instâncias de ObjectType)
        self.conn.execute(
            """
            CREATE NODE TABLE IF NOT EXISTS Object (
                rid STRING,
                object_type_rid STRING,
                primary_key_value STRING,
                properties STRING,
                PRIMARY KEY (rid)
            )
        """
        )

        # Criar REL TABLE para LinkedObject (instâncias de LinkType)
        self.conn.execute(
            """
            CREATE REL TABLE IF NOT EXISTS LinkedObject (
                FROM Object TO Object,
                rid STRING,
                link_type_rid STRING,
                properties STRING
            )
        """
        )

        print("INFO: Schema do KuzuDB pronto.")

    def is_available(self) -> bool:
        """Retorna True se KuzuDB está disponível e conectado."""
        return self.conn is not None

    def execute(self, query: str):
        """
        Executa uma query Cypher no KuzuDB.

        Args:
            query: Query Cypher

        Returns:
            Query result

        Raises:
            RuntimeError: Se KuzuDB não estiver disponível
        """
        if not self.is_available():
            raise RuntimeError("KuzuDB não está disponível")

        return self.conn.execute(query)

    def close(self):
        """Fecha a conexão (geralmente chamado no shutdown da aplicação)."""
        if self.conn:
            self.conn.close()
            print("INFO: Conexão KuzuDB fechada.")


def get_kuzu_repo() -> KuzuDBRepository:
    """
    Função de dependência do FastAPI para injetar o repositório KuzuDB.

    Uso em endpoints:
        @app.get("/graph/query")
        def query_graph(repo: KuzuDBRepository = Depends(get_kuzu_repo)):
            ...
    """
    return KuzuDBRepository()
