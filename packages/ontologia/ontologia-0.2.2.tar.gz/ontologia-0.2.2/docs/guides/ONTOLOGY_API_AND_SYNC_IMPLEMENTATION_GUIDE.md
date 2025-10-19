# Guia de Implementação – API de Metadados e Serviço de Sincronização
- Público-alvo: Equipe de Desenvolvimento
- Objetivo: Consolidar a arquitetura da API (Fase 1) e orientar a implementação do Serviço de Sincronização (início da Fase 2)

---

  ## 1) Visão Geral da Arquitetura

  - **registro (lib core)**: identidade de recursos (RID), multi-tenancy (`service`, `instance`).
  - **datacatalog (lib)**: descreve dados físicos (Datasets). Origem das tabelas/arquivos brutos.
  - **ontologia (lib)**: modelo semântico (tipos e relações) e mapeamentos de origem.
  - **api (FastAPI)**: interface REST para metamodelo e (futuro) instâncias/consultas.
  - **sync.py (worker)**: orquestra a materialização do grafo no KùzuDB a partir do metamodelo + dados físicos.

Arquitetura multicamadas (implementada):
- **Apresentação**: routers em `api/v2/routers/` (magros, HTTP puro).
- **Serviço**: `api/services/metamodel_service.py` (regras de negócio, upsert, validações).

## 3) Tarefa Prioritária – OntologySyncService (início Fase 2)

Por quê: transformar o metamodelo (semântico) + datacatalog (físico) em grafo consultável (Kùzu).

  Local sugerido:
  - Serviço: `ontologia/application/sync_service.py`
  - Runner/CLI: `scripts/main_sync.py`

Dependências (opcionais, para o worker): `kuzu`, `duckdb`, `polars`.

Modelos de entrada (metadados):
- `ontologia/domain/metamodels/types/object_type.py::ObjectType`
{{ ... }}
- `ontologia/domain/metamodels/instances/object_type_data_source.py::ObjectTypeDataSource` (associa OT ↔ Dataset)
- `datacatalog.models::Dataset` (fora deste repo; esperado na stack)

### 3.1) Responsabilidades do Sync
- Construir (ou validar) o schema do grafo no Kùzu a partir dos `ObjectType`/`LinkType`.
- Conectar ao ambiente de dados (DuckDB, Parquet, etc.).
- Carregar dados físicos → nós (Objects) por `ObjectType`.
- (Próximo) Carregar relações → arestas (LinkedObject) por `LinkType`.
- Idempotente e seguro para re-execução.

### 3.2) Fluxo proposto
1. Ler metamodelo pelo SQLModel (`Session(engine)`): listar `ObjectType`, `PropertyType`, `LinkType` e `ObjectTypeDataSource`.
2. Criar/validar tabelas de nós/arestas no Kùzu (`CREATE NODE/REL TABLE IF NOT EXISTS`).
3. Anexar DuckDB ao Kùzu (ou ler via DuckDB/Polars e usar API de COPY/LOAD do Kùzu).
4. Para cada `ObjectType` com fontes (`data_sources`):
   - Ler datasets (ex.: `duckdb_table`).
   - Aplicar mappings via `ObjectTypeDataSource.property_mappings` (ex.: `emp_id → id`).
   - Unificar múltiplas fontes; deduplicar por PK.
   - Carregar no nó do Kùzu.
5. Para cada `LinkType`:
   - Preferir dataset configurado em `LinkType.backing_dataset_rid` (join dataset). Se ausente, usar convenção `{linkTypeApiName}_rels`.
   - Colunas: usar `from_property_mapping` e `to_property_mapping` quando definidos; caso contrário, `from_{fromPK}`/`to_{toPK}` (ex.: `from_id`, `to_id`).
   - `property_mappings` (JSON) pode mapear colunas adicionais do dataset para propriedades do link.
   - Carregar `REL` com chaves de origem/destino resolvidas.

### 3.3) Esqueleto do serviço (exemplo)

```python
# ontologia/application/sync_service.py
from typing import Dict, List
import logging
from sqlmodel import Session, select

from ontologia.domain.metamodels.types.object_type import ObjectType
from ontologia.domain.metamodels.types.link_type import LinkType
from ontologia.domain.metamodels.instances.object_type_data_source import ObjectTypeDataSource

logger = logging.getLogger(__name__)

class OntologySyncService:
    def __init__(self, meta_session: Session, kuzu_conn, duckdb_conn, *, type_mapping: Dict[str, str] | None = None):
        self.meta = meta_session
        self.kuzu = kuzu_conn  # kuzu.Connection
        self.duck = duckdb_conn  # duckdb.DuckDBPyConnection
        self.type_mapping = type_mapping or {
            "string": "STRING", "integer": "INT64", "double": "DOUBLE",
            "boolean": "BOOL", "date": "DATE", "timestamp": "TIMESTAMP",
        }

    def sync_all(self, duckdb_path: str | None = None):
        logger.info("Iniciando sync da ontologia...")
        self._ensure_graph_schema()
        if duckdb_path:
            self._attach_duckdb(duckdb_path)
        self._load_nodes()
        # TODO: self._load_rels()
        logger.info("Sync concluído com sucesso.")

    def _ensure_graph_schema(self):
        # Nodes por ObjectType
        for ot in self.meta.exec(select(ObjectType)).all():
            cols = [f"{p.api_name} {self.type_mapping.get(p.data_type, 'STRING')}" for p in ot.property_types]
            cols.append(f"PRIMARY KEY ({ot.primary_key_field})")
            self.kuzu.execute(f"CREATE NODE TABLE IF NOT EXISTS {ot.api_name} ({', '.join(cols)});")
        # Rels por LinkType
        for lt in self.meta.exec(select(LinkType)).all():
            self.kuzu.execute(
                f"CREATE REL TABLE IF NOT EXISTS {lt.api_name} (FROM {lt.from_object_type_api_name} TO {lt.to_object_type_api_name});"
            )

    def _attach_duckdb(self, duckdb_path: str):
        try:
            self.kuzu.execute(f"ATTACH '{duckdb_path}' AS duckdb (dbtype 'duckdb');")
        except Exception as e:
            logger.warning("DuckDB já anexado ou indisponível: %s", e)

    def _load_nodes(self):
        object_types: List[ObjectType] = self.meta.exec(select(ObjectType)).all()
        for ot in object_types:
            if not ot.data_sources:
                logger.info("Sem fontes para '%s' – ignorando.", ot.api_name)
                continue
            # TODO: ler datasets via DuckDB/Polars, aplicar mappings e carregar no Kùzu
            logger.info("Preparando carga de nós para '%s'...", ot.api_name)
```

Notas:
- O exemplo acima usa imports do seu tree atual (ontologia/domain/...); ajuste conforme consolidarmos o pacote `datacatalog`.
- O serviço deve ser idempotente; use `IF NOT EXISTS` e chaves primárias corretas.
- Evitar dependências no servidor da API; execute o sync em processo separado.
- `ObjectTypeDataSource.property_mappings` é um JSON (dataset column → OT property), ex.: `{ "emp_id": "id", "name": "name" }`.
- Relações: `LinkType` expõe `backing_dataset_rid`, `from_property_mapping`, `to_property_mapping` e `property_mappings` para carga dirigida por metadados; há fallback para `{linkType}_rels` com `from_*/to_*`.

### 3.4) Orquestração (runner)

```python
# scripts/main_sync.py (exemplo de runner)
import duckdb, kuzu, logging
from sqlmodel import Session
from api.core.database import engine
from ontologia.application.sync_service import OntologySyncService

logging.basicConfig(level=logging.INFO)

with Session(engine) as s:
    db = kuzu.Database(database_path="instance_graph.kuzu")
    kc = kuzu.Connection(db)
    dd = duckdb.connect(database=":memory:")
    OntologySyncService(s, kc, dd).sync_all(duckdb_path="/path/para/duckdb.db")
```

---

### 3.5) Setup do Plano de Controle via Services (exemplos)

Flag de carga de relações (COPY):
- `SYNC_ENABLE_COPY_RELS=1` habilita o caminho de COPY no `OntologySyncService._load_rels_into_graph()` quando `DuckDB` está anexado, usando `LinkType.backing_dataset_rid` e `from_property_mapping`/`to_property_mapping`.
- Formato emitido: `COPY {linkType} FROM duckdb.{dataset.source_identifier} (FROM {from_col} TO {to_col});`
- Fallback permanece (comando placeholder) quando a flag está desligada ou sem DuckDB/Polars.

Reconciliação de propriedades:
- Centralizada em `api/services/metamodel_service.py::MetamodelService.upsert_object_type()`.
- O método `ObjectType.set_properties()` foi removido do modelo. O service é a fonte única da verdade (conta deletados/atualizados/criados e loga a duração).


```python
from api.services.metamodel_service import MetamodelService
from datacatalog.models import TransactionType

svc = MetamodelService(session, service="ontology", instance="default")

# Dataset físico
ds = svc.upsert_dataset(
    api_name="employees_ds",
    source_type="duckdb_table",
    source_identifier="employees_tbl",
    display_name="Employees DS",
)

# Vincular Dataset a um ObjectType
svc.add_data_source_to_object_type(
    object_type_api_name="employee",
    dataset_api_name="employees_ds",
    property_mappings={"emp_id": "id", "name_col": "name"},
)

# Transação e branch (opcional)
commit = svc.create_transaction("employees_ds", transaction_type=TransactionType.SNAPSHOT, commit_message="Initial snapshot")
branch = svc.create_branch("employees_ds", branch_name="main", head_transaction_rid=commit.rid)
```

---

## 4) Critérios de Aceite

- **Schema**: criação idempotente de NODE/REL no Kùzu coerente com `ObjectType`/`LinkType`.
- **Carga de nós**: unificação de múltiplas fontes por PK; mappings aplicados.
- **Observabilidade**: logs claros por fase (schema, anexação, carga).
- **Isolamento**: execução fora do processo da API; sem bloquear requests.
- **Testes de fumaça**: ao menos um OT com `ObjectTypeDataSource` carregado no Kùzu.

---

## 5) Como Executar (Fase 1)

- **API**: `uvicorn api.main:app --reload`
- **Variáveis**:
  - `DATABASE_URL` (SQLite padrão: `sqlite:///metamodel.db`; Postgres suportado)
  - `KUZU_DB_PATH` (padrão em `api/repositories/kuzudb_repository.py`)
- **Health**: `GET /health` retorna status do DB e do Kùzu.

---

## 6) Próximos Passos (Fase 2)

- **Instances API**: CRUD de instâncias (`objects`) e links (`linkedObjects`).
- **Query Engine**: DSL segura com execução híbrida (SQL metadata + Kùzu/Cypher).
- **Sync (rels)**: completar `_load_rels()` com mapeamentos `from`/`to` e validações de cardinalidade.
- **Auth/Observabilidade/CI**: JWT + RBAC, métricas/logs estruturados, GH Actions (ruff/black/pytest).

---

## 7) Referências de Código

- Serviço: `api/services/metamodel_service.py`
- Repositório: `api/repositories/metamodel_repository.py`
- Modelos: `ontologia/domain/metamodels/types/{object_type,property_type,link_type}.py`
- Mapeamento de fontes: `ontologia/domain/metamodels/instances/object_type_data_source.py`
- API: `api/v2/routers/{object_types,link_types}.py`
- App e health: `api/main.py`
- Kùzu repo: `api/repositories/kuzudb_repository.py`
- Testes: `tests/` (unit + integração)
