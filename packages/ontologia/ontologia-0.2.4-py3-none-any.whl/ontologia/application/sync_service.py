"""
sync_service.py
---------------
OntologySyncService: Motor ETL que materializa o grafo de conhecimento.

Este serviço é responsável por:
1. Ler metadados do Plano de Controle (ontologia + datacatalog)
2. Extrair dados do Plano de Dados Brutos (DuckDB/Parquet)
3. Transformar e unificar dados conforme o modelo semântico
4. Carregar no Plano Semântico (KùzuDB) otimizado para consultas

Analogia:
- Plano de Controle = Livro de Receitas (ObjectType = receita do "Bolo")
- Plano de Dados Brutos = Ingredientes na Despensa (farinha, ovos)
- OntologySyncService = Chef (lê, prepara, assa)
- Plano Semântico = Bolo Pronto (pronto para servir/consultar)
"""

import importlib.util
import json
import logging
import os
from datetime import datetime
from typing import Any

from sqlmodel import Session, select

from datacatalog.models import Dataset
from ontologia.config import load_config
from ontologia.domain.metamodels.types.link_type import LinkType
from ontologia.domain.metamodels.types.object_type import ObjectType

KUZU_AVAILABLE = importlib.util.find_spec("kuzu") is not None
if not KUZU_AVAILABLE:
    logging.warning("KùzuDB não instalado. Install com: pip install kuzu")

DUCKDB_AVAILABLE = importlib.util.find_spec("duckdb") is not None
if not DUCKDB_AVAILABLE:
    logging.warning("DuckDB não instalado. Install com: pip install duckdb")

try:
    import polars as pl

    POLARS_AVAILABLE = True
except ImportError:
    POLARS_AVAILABLE = False
    logging.warning("Polars não instalado. Install com: pip install polars")

# Configura o logger
logger = logging.getLogger(__name__)


class SyncMetrics:
    """Métricas de sincronização para monitoramento."""

    def __init__(self):
        self.start_time: datetime | None = None
        self.end_time: datetime | None = None
        self.nodes_created: dict[str, int] = {}
        self.rels_created: dict[str, int] = {}
        self.errors: list[str] = []
        self.warnings: list[str] = []
        # Data quality metrics por ObjectType
        self.total_rows_read: dict[str, int] = {}
        self.clean_rows_loaded: dict[str, int] = {}
        self.quarantined_rows: dict[str, int] = {}

    def start(self):
        """Marca o início da sincronização."""
        self.start_time = datetime.now()

    def finish(self):
        """Marca o fim da sincronização."""
        self.end_time = datetime.now()

    def duration(self) -> float:
        """Retorna a duração em segundos."""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0.0

    def add_nodes(self, object_type: str, count: int):
        """Registra nós criados."""
        self.nodes_created[object_type] = count

    def add_rels(self, link_type: str, count: int):
        """Registra relações criadas."""
        self.rels_created[link_type] = count

    def add_error(self, error: str):
        """Registra um erro."""
        self.errors.append(error)

    def add_warning(self, warning: str):
        """Registra um aviso."""
        self.warnings.append(warning)

    def summary(self) -> str:
        """Retorna um resumo das métricas."""
        lines = [
            "=" * 60,
            "SYNC METRICS SUMMARY",
            "=" * 60,
            f"Duration: {self.duration():.2f}s",
            f"Nodes Created: {sum(self.nodes_created.values())}",
        ]

        for obj_type, count in self.nodes_created.items():
            lines.append(f"  - {obj_type}: {count}")

        lines.append(f"Relations Created: {sum(self.rels_created.values())}")

        for link_type, count in self.rels_created.items():
            lines.append(f"  - {link_type}: {count}")

        # Data quality summary
        if self.total_rows_read:
            lines.append("Data Quality:")
            for ot, total in self.total_rows_read.items():
                clean = self.clean_rows_loaded.get(ot, 0)
                quarantined = self.quarantined_rows.get(ot, 0)
                rate = (clean / total * 100.0) if total else 0.0
                lines.append(
                    f"  - {ot}: total={total} clean={clean} quarantined={quarantined} ok_rate={rate:.1f}%"
                )

        if self.warnings:
            lines.append(f"Warnings: {len(self.warnings)}")
            for warning in self.warnings[:5]:  # Mostrar até 5 warnings
                lines.append(f"  - {warning}")

        if self.errors:
            lines.append(f"Errors: {len(self.errors)}")
            for error in self.errors[:5]:  # Mostrar até 5 erros
                lines.append(f"  - {error}")

        lines.append("=" * 60)
        return "\n".join(lines)


class OntologySyncService:
    """
    Serviço responsável por ler o Plano de Controle (metadados) e sincronizar
    os dados de um Plano de Dados Brutos (DuckDB/Parquet) para um
    Plano Semântico otimizado para consulta (KùzuDB).

    Arquitetura:

    ┌─────────────────────────────────┐
    │   PLANO DE CONTROLE             │
    │   (ontologia + datacatalog)     │
    │   - ObjectType                  │
    │   - LinkType                    │
    │   - Dataset                     │
    └─────────────────────────────────┘
              ↓ (lê metadados)
    ┌─────────────────────────────────┐
    │   ONTOLOGY SYNC SERVICE         │
    │   (ETL)                         │
    └─────────────────────────────────┘
              ↓ (extrai/transforma)
    ┌─────────────────────────────────┐
    │   PLANO DE DADOS BRUTOS         │
    │   (DuckDB/Parquet)              │
    └─────────────────────────────────┘
              ↓ (carrega)
    ┌─────────────────────────────────┐
    │   PLANO SEMÂNTICO               │
    │   (KùzuDB - Grafo)              │
    └─────────────────────────────────┘
    """

    def __init__(
        self,
        metadata_session: Session,
        kuzu_conn=None,  # kuzu.Connection
        duckdb_conn=None,  # duckdb.DuckDBPyConnection
    ):
        """
        Inicializa o serviço de sincronização.

        Args:
            metadata_session: Sessão SQLModel para acessar metadados
            kuzu_conn: Conexão KùzuDB para o grafo semântico
            duckdb_conn: Conexão DuckDB para dados brutos
        """
        # Permite injeção de mocks mesmo sem os pacotes instalados (facilita testes)
        if not KUZU_AVAILABLE and kuzu_conn is not None:
            logger.warning(
                "KùzuDB não instalado, mas uma conexão foi fornecida; prosseguindo em modo de teste."
            )
        if not DUCKDB_AVAILABLE and duckdb_conn is not None:
            logger.warning(
                "DuckDB não instalado, mas uma conexão foi fornecida; prosseguindo em modo de teste."
            )

        if not POLARS_AVAILABLE:
            logger.warning(
                "Polars não está instalado. Funcionalidades de sync limitadas. Install com: pip install polars"
            )

        self.meta_db = metadata_session
        self.kuzu = kuzu_conn
        self.duckdb = duckdb_conn
        self.metrics = SyncMetrics()

        config = load_config()
        if not config.features.use_unified_graph:
            logger.warning(
                "Modo de grafo unificado agora é obrigatório; ignorando features.use_unified_graph = false."
            )
        env_override = os.getenv("USE_UNIFIED_GRAPH")
        if env_override and env_override not in ("1", "true", "True"):
            logger.warning(
                "Modo de grafo unificado agora é obrigatório; ignorando USE_UNIFIED_GRAPH=%s.",
                env_override,
            )

        # Mapeamento de tipos de dados ontologia → KùzuDB
        self.type_mapping: dict[str, str] = {
            "string": "STRING",
            "integer": "INT64",
            "int": "INT64",
            "long": "INT64",
            "double": "DOUBLE",
            "float": "DOUBLE",
            "boolean": "BOOL",
            "bool": "BOOL",
            "date": "DATE",
            "timestamp": "TIMESTAMP",
        }

    def sync_ontology(self, duckdb_path: str | None = None) -> SyncMetrics:
        """
        Orquestra o processo completo de sincronização da ontologia.

        Passos:
        1. Construir o esquema do grafo no KùzuDB
        2. Anexar DuckDB (se fornecido)
        3. Carregar dados nos nós
        4. Carregar dados nas relações

        Args:
            duckdb_path: Caminho para o arquivo DuckDB (opcional)

        Returns:
            SyncMetrics com estatísticas da sincronização
        """
        self.metrics.start()
        logger.info("🚀 Iniciando sincronização completa da ontologia...")

        try:
            # Passo 1: Construir esquema
            self._build_graph_schema()

            # Passo 2: Anexar DuckDB se fornecido
            if duckdb_path and self.kuzu:
                self._attach_duckdb(duckdb_path)

            # Passo 3: Carregar nós
            self._load_nodes_into_graph()

            # Passo 4: Carregar relações
            self._load_rels_into_graph()

            logger.info("✅ Sincronização da ontologia concluída com sucesso!")

        except Exception as e:
            error_msg = f"Erro durante sincronização: {e}"
            logger.error(error_msg)
            self.metrics.add_error(error_msg)
            raise

        finally:
            self.metrics.finish()

        # Imprimir resumo
        logger.info("\n" + self.metrics.summary())

        return self.metrics

    def _build_graph_schema(self):
        """
        Lê o metamodelo e constrói o esquema de nós e arestas no KùzuDB.

        Cria o modelo unificado: uma NODE TABLE `Object` com propriedades JSON e
        REL TABLEs entre `Object`→`Object` para cada LinkType.
        """
        logger.info("--- 1. Construindo Esquema do Grafo no KùzuDB ---")

        if not self.kuzu:
            logger.warning("  KùzuDB não configurado, pulando construção do esquema")
            return

        try:
            cypher_object = (
                "CREATE NODE TABLE Object ("
                " rid STRING,"
                " objectTypeApiName STRING,"
                " pkValue STRING,"
                " labels STRING[],"
                " properties STRING,"
                " PRIMARY KEY (rid)"
                ");"
            )
            logger.info(f"  Executando: {cypher_object}")
            self.kuzu.execute(cypher_object)
            for index_field in ("objectTypeApiName", "pkValue", "rid"):
                try:
                    self.kuzu.execute(f"CREATE INDEX ON Object({index_field});")
                except Exception as e:
                    self.metrics.add_warning(f"Falha ao criar índice {index_field} em Object: {e}")
        except Exception as e:
            warning = f"Erro ao criar NODE TABLE unificada 'Object': {e}"
            logger.warning(warning)
            self.metrics.add_warning(warning)

        link_types = self.meta_db.exec(select(LinkType)).all()
        for lt in link_types:
            try:
                props_parts: list[str] = []
                for link_prop in getattr(lt, "link_property_types", []) or []:
                    kuzu_type = self.type_mapping.get(str(link_prop.data_type).lower(), "STRING")
                    props_parts.append(f"{link_prop.api_name} {kuzu_type}")
                props_str = (", " + ", ".join(props_parts)) if props_parts else ""
                cypher_rel = f"CREATE REL TABLE {lt.api_name} (FROM Object TO Object{props_str});"
                logger.info(f"  Executando: {cypher_rel}")
                self.kuzu.execute(cypher_rel)
            except Exception as e:
                warning = f"Erro ao criar REL TABLE '{lt.api_name}': {e}"
                logger.warning(warning)
                self.metrics.add_warning(warning)

    def _attach_duckdb(self, duckdb_path: str):
        """
        Anexa o banco de dados DuckDB à conexão Kùzu para permitir a cópia direta.

        Args:
            duckdb_path: Caminho para o arquivo DuckDB
        """
        logger.info("--- 2. Anexando DuckDB ao KùzuDB ---")

        if not self.kuzu:
            logger.warning("  KùzuDB não configurado, pulando anexação")
            return

        try:
            attach_cmd = f"ATTACH '{duckdb_path}' AS duckdb (dbtype 'duckdb');"
            logger.info(f"  Executando: {attach_cmd}")
            self.kuzu.execute(attach_cmd)
            logger.info("  ✅ DuckDB anexado com sucesso")
        except Exception as e:
            warning = f"Erro ao anexar DuckDB (pode já estar anexado): {e}"
            logger.warning(warning)
            self.metrics.add_warning(warning)

    def _load_nodes_into_graph(self):
        """
        Carrega e unifica dados de múltiplos datasets para popular os nós do grafo.

        Para cada ObjectType:
        1. Encontra todas as suas fontes (ObjectTypeDataSource)
        2. Lê dados de cada fonte usando Polars
        3. Aplica mapeamentos de propriedades
        4. Une (UNION) todos os dados
        5. Remove duplicatas pela chave primária
        6. Carrega em lote no KùzuDB
        """
        logger.info("--- 3. Carregando Dados nos Nós ---")

        if not self.kuzu:
            logger.warning("  KùzuDB não configurado, pulando carga de nós")
            return

        # Buscar ObjectTypes que têm fontes de dados
        object_types = self.meta_db.exec(select(ObjectType)).all()

        for ot in object_types:
            if not ot.data_sources:
                logger.info(f"  ⏭️  ObjectType '{ot.api_name}' não tem fontes de dados, pulando")
                continue

            try:
                dataframes_to_union = []
                logger.info(f"  📊 Processando ObjectType: '{ot.api_name}'...")

                for data_source_link in ot.data_sources:
                    # Resolve dataset via branch head transaction (Time Travel),
                    # falling back to legacy direct dataset linkage
                    dataset = None
                    branch = getattr(data_source_link, "dataset_branch", None)
                    if branch is not None:
                        head_tx = getattr(branch, "head_transaction", None)
                        if head_tx is not None and getattr(head_tx, "dataset", None) is not None:
                            dataset = head_tx.dataset
                        elif getattr(branch, "dataset", None) is not None:
                            dataset = branch.dataset
                    if dataset is None:
                        # Legacy path
                        dataset = getattr(data_source_link, "dataset", None)
                    if dataset is None:
                        self.metrics.add_warning(
                            f"Fonte de dados não resolvida para '{ot.api_name}' (branch/dataset ausente)"
                        )
                        continue
                    mappings = getattr(data_source_link, "property_mappings", None) or {}

                    logger.info(
                        f"    - Lendo do Dataset '{dataset.api_name}' ({dataset.source_type})..."
                    )

                    # Ler dados dependendo do source_type
                    raw_df = self._read_dataset(dataset)

                    if raw_df is None:
                        continue

                    # Incremental APPEND filter if configured
                    try:
                        incr_field = getattr(data_source_link, "incremental_field", None)
                        last_sync = getattr(data_source_link, "last_sync_time", None)
                        if (
                            incr_field
                            and last_sync
                            and POLARS_AVAILABLE
                            and incr_field in getattr(raw_df, "columns", [])
                        ):
                            try:
                                ts = last_sync
                                raw_df = raw_df.filter(pl.col(incr_field) > pl.lit(ts))
                            except Exception as e:
                                self.metrics.add_warning(
                                    f"Falha no filtro incremental para '{ot.api_name}': {e}"
                                )
                    except Exception:
                        pass

                    # Aplicar mapeamentos de colunas (legado)
                    # Quando SYNC_ASSUME_GOLD_SCHEMA=1, assumimos que as colunas
                    # já estão padronizadas pelas transformações (DBT/Gold) e pulamos renomeações.
                    if mappings and os.getenv("SYNC_ASSUME_GOLD_SCHEMA", "0") not in (
                        "1",
                        "true",
                        "True",
                    ):
                        raw_df = raw_df.rename(mappings)

                    # Garantir que o schema está consistente
                    final_props = [p.api_name for p in ot.property_types]
                    available_props = [p for p in final_props if p in raw_df.columns]

                    if available_props:
                        selected_df = raw_df.select(available_props)
                        dataframes_to_union.append(selected_df.lazy())

                if not dataframes_to_union:
                    warning = f"Nenhuma fonte de dados processável para '{ot.api_name}'"
                    logger.warning(f"    - {warning}")
                    self.metrics.add_warning(warning)
                    continue

                # Unir todos os dataframes e remover duplicatas
                unified_df = (
                    pl.concat(dataframes_to_union)
                    .unique(subset=[ot.primary_key_field], keep="last")
                    .collect()
                )
                # Data Quality: aplicar regras de qualidade por propriedade
                clean_df = unified_df
                quarantine_df = None
                total_rows = len(unified_df)
                if POLARS_AVAILABLE and total_rows > 0:
                    try:
                        valid_expr = pl.lit(True)
                        # Apenas aplica checagens para colunas existentes
                        cols_set = set(unified_df.columns)
                        for prop_type in ot.property_types:
                            checks = getattr(prop_type, "quality_checks", None) or []
                            if not checks:
                                continue
                            col_name = prop_type.api_name
                            if col_name not in cols_set:
                                self.metrics.add_warning(
                                    f"Qualidade: coluna '{col_name}' não encontrada para '{ot.api_name}', ignorando checks"
                                )
                                continue
                            for chk in checks:
                                chk = str(chk).strip()
                                if chk == "not_null":
                                    valid_expr = valid_expr & pl.col(col_name).is_not_null()
                                elif chk.startswith("in[") and chk.endswith("]"):
                                    inside = chk[3:-1]
                                    options = [
                                        s.strip() for s in inside.split(",") if s.strip() != ""
                                    ]
                                    valid_expr = valid_expr & pl.col(col_name).is_in(options)
                                elif chk.startswith("between[") and chk.endswith("]"):
                                    inside = chk[len("between[") : -1]
                                    parts = [p.strip() for p in inside.split(",")]
                                    if len(parts) == 2:
                                        lo, hi = parts[0], parts[1]
                                        # tenta converter para número quando possível
                                        valid_expr = valid_expr & (
                                            pl.col(col_name)
                                            >= pl.lit(lo) & pl.col(col_name)
                                            <= pl.lit(hi)
                                        )
                                elif chk.startswith("min_length[") and chk.endswith("]"):
                                    n = int(chk[len("min_length[") : -1])
                                    valid_expr = valid_expr & (
                                        pl.col(col_name).cast(pl.Utf8, strict=False).str.len_chars()
                                        >= n
                                    )
                                elif chk.startswith("max_length[") and chk.endswith("]"):
                                    n = int(chk[len("max_length[") : -1])
                                    valid_expr = valid_expr & (
                                        pl.col(col_name).cast(pl.Utf8, strict=False).str.len_chars()
                                        <= n
                                    )
                        # Split datasets
                        clean_df = unified_df.filter(valid_expr)
                        quarantine_df = unified_df.filter(~valid_expr)
                    except Exception as e:
                        self.metrics.add_warning(
                            f"Falha nas checagens de qualidade para '{ot.api_name}': {e}"
                        )
                        clean_df = unified_df
                        quarantine_df = None

                # Registrar métricas DQ
                self.metrics.total_rows_read[ot.api_name] = int(total_rows)
                self.metrics.clean_rows_loaded[ot.api_name] = int(len(clean_df))
                self.metrics.quarantined_rows[ot.api_name] = (
                    int(len(quarantine_df)) if quarantine_df is not None else 0
                )

                # Exportar quarentena, se existir
                try:
                    if quarantine_df is not None and len(quarantine_df) > 0:
                        out_dir = os.path.join("data", "quarantine")
                        os.makedirs(out_dir, exist_ok=True)
                        ts = datetime.now().strftime("%Y%m%dT%H%M%S")
                        out_path = os.path.join(out_dir, f"{ot.api_name}-{ts}.parquet")
                        quarantine_df.write_parquet(out_path)
                        logger.warning(
                            f"    - Dados em quarentena para '{ot.api_name}': {len(quarantine_df)} linhas → {out_path}"
                        )
                except Exception as e:
                    self.metrics.add_warning(
                        f"Falha ao exportar quarentena para '{ot.api_name}': {e}"
                    )

                try:
                    logger.info(
                        f"    - 📥 Preparando carga para o nó unificado 'Object' com '{ot.api_name}'..."
                    )
                    labels = [ot.api_name] + [
                        it.api_name for it in getattr(ot, "interfaces", []) or []
                    ]
                    pk_field = ot.primary_key_field
                    service_name = getattr(ot, "service", "ontology")
                    instance_name = getattr(ot, "instance", "default")
                    items_lits: list[str] = []
                    for rec in clean_df.to_dicts():  # type: ignore[attr-defined]
                        pk_val = rec.get(pk_field)
                        if pk_val is None:
                            self.metrics.add_warning(
                                f"Objeto sem PK '{pk_field}' encontrado para '{ot.api_name}', ignorando linha."
                            )
                            continue
                        rid = f"{service_name}:{instance_name}:{ot.api_name}:{pk_val}"
                        props_json = json.dumps(rec, default=str)
                        props_json_escaped = props_json.replace("'", "''")
                        labels_lit = "[" + ", ".join([f"'{label}'" for label in labels]) + "]"
                        items_lits.append(
                            "{ rid: '"
                            + rid
                            + "', objectTypeApiName: '"
                            + ot.api_name
                            + "', pkValue: '"
                            + str(pk_val)
                            + "', labels: "
                            + labels_lit
                            + ", properties: '"
                            + props_json_escaped
                            + "' }"
                        )

                    if not items_lits:
                        logger.info(
                            f"    - Nenhum registro válido para carregar em '{ot.api_name}'."
                        )
                        continue

                    items_arr = "[" + ", ".join(items_lits) + "]"
                    cypher = (
                        f"UNWIND {items_arr} AS row "
                        f"MERGE (o:Object {{ rid: row.rid }}) "
                        f"SET o.objectTypeApiName = row.objectTypeApiName, o.labels = row.labels, o.properties = row.properties, o.pkValue = row.pkValue"
                    )
                    self.kuzu.execute(cypher)
                    self.metrics.add_nodes(ot.api_name, len(items_lits))
                    logger.info("    - ✅ Carregamento concluído (unificado)!")
                except Exception as e:
                    error = f"Falha no carregamento unificado para '{ot.api_name}': {e}"
                    logger.error(f"    - ❌ {error}")
                    self.metrics.add_error(error)
                    continue

                # Registrar lineage: última transação sincronizada por fonte (se houver branch)
                try:
                    for data_source_link in ot.data_sources:
                        branch = getattr(data_source_link, "dataset_branch", None)
                        if branch and getattr(branch, "head_transaction_rid", None):
                            data_source_link.last_synced_transaction_rid = (
                                branch.head_transaction_rid
                            )
                        # Atualizar last_sync_time para agora após carga
                        try:
                            data_source_link.last_sync_time = datetime.now()
                        except Exception:
                            pass
                        data_source_link.last_sync_time = datetime.now()
                        data_source_link.sync_status = "completed"
                        self.meta_db.add(data_source_link)
                    self.meta_db.commit()
                except Exception as e:
                    self.metrics.add_warning(
                        f"Falha ao persistir lineage de sync para '{ot.api_name}': {e}"
                    )

            except Exception as e:
                error = f"Erro ao carregar nós para '{ot.api_name}': {e}"
                logger.error(f"    - ❌ {error}")
                self.metrics.add_error(error)

    def _read_dataset(self, dataset: Dataset) -> Any | None:
        """
        Lê dados de um Dataset usando Polars.

        Suporta:
        - duckdb_table: Lê de uma tabela DuckDB
        - parquet_file: Lê de um arquivo Parquet

        Args:
            dataset: Dataset a ser lido

        Returns:
            DataFrame Polars ou None se erro
        """
        try:
            if not POLARS_AVAILABLE:
                logger.warning(
                    "      Polars não está disponível; leitura de datasets será ignorada."
                )
                return None
            if dataset.source_type == "duckdb_table":
                if not self.duckdb:
                    logger.warning(
                        f"      DuckDB não configurado, não pode ler '{dataset.api_name}'"
                    )
                    return None

                query = f"SELECT * FROM {dataset.source_identifier}"
                return pl.read_database(query, self.duckdb)

            elif dataset.source_type == "parquet_file":
                # Lê diretamente do arquivo Parquet
                return pl.read_parquet(dataset.source_identifier)

            else:
                warning = f"Source type '{dataset.source_type}' não suportado ainda"
                logger.warning(f"      {warning}")
                self.metrics.add_warning(warning)
                return None

        except Exception as e:
            error = f"Erro ao ler dataset '{dataset.api_name}': {e}"
            logger.error(f"      ❌ {error}")
            self.metrics.add_error(error)
            return None

    def _load_rels_into_graph(self):
        """
        Carrega dados de datasets de junção para popular as relações do grafo.

        Convenção provisória (até existir LinkTypeDataSource):
        - Se existir um Dataset com api_name "{linkTypeApiName}_rels", ele é usado
        - Espera colunas: "from_{from_pk}", "to_{to_pk}", onde from_pk/to_pk são as PKs
          dos ObjectTypes de origem/destino (ex.: from_id, to_id)
        - Realiza carga chamando self.kuzu.execute com comando COPY/INSERT (mockado em testes)
        """
        logger.info("--- 4. Carregando Dados nas Relações ---")

        if not self.kuzu:
            logger.warning("  KùzuDB não configurado, pulando carga de relações")
            return

        link_types = self.meta_db.exec(select(LinkType)).all()

        # Import local para evitar dependência dura quando não usado
        from datacatalog.models import Dataset

        for lt in link_types:
            try:
                # Determinar PKs dos OTs de origem/destino (para fallback convencional)
                from_pk = None
                to_pk = None
                if lt.from_object_type_api_name:
                    from_ot = self.meta_db.exec(
                        select(ObjectType).where(
                            ObjectType.api_name == lt.from_object_type_api_name
                        )
                    ).first()
                    from_pk = from_ot.primary_key_field if from_ot else None
                if lt.to_object_type_api_name:
                    to_ot = self.meta_db.exec(
                        select(ObjectType).where(ObjectType.api_name == lt.to_object_type_api_name)
                    ).first()
                    to_pk = to_ot.primary_key_field if to_ot else None
                if not from_pk or not to_pk:
                    self.metrics.add_warning(
                        f"PK ausente para '{lt.api_name}', pulando carga de relações"
                    )
                    continue

                # Caminho 1: usar backing_dataset_rid com mapeamentos explícitos
                if getattr(lt, "backing_dataset_rid", None):
                    if not (lt.from_property_mapping and lt.to_property_mapping):
                        logger.warning(
                            f"    - Pulando '{lt.api_name}': from/to property mappings não definidos."
                        )
                        continue
                    ds = self.meta_db.get(Dataset, lt.backing_dataset_rid)
                    if not ds:
                        logger.warning(
                            f"    - Pulando '{lt.api_name}': backing dataset não encontrado."
                        )
                        continue
                    if ds.source_type != "duckdb_table":
                        logger.warning(
                            f"    - Pulando '{lt.api_name}': backing dataset não é 'duckdb_table'."
                        )
                        continue
                    from_col = lt.from_property_mapping
                    to_col = lt.to_property_mapping
                    # Modo COPY real (feature flag)
                    if os.getenv("SYNC_ENABLE_COPY_RELS", "0") in ("1", "true", "True"):
                        props_clause = ""
                        link_props = getattr(lt, "property_mappings", None) or {}
                        if link_props:
                            props_mapping_str = ", ".join(
                                [f"{k} = {v}" for k, v in link_props.items()]
                            )
                            props_clause = f", PROPERTIES ({props_mapping_str})"
                        # Optional incremental filter via DuckDB view is not applied in COPY mode.
                        cypher = (
                            f"COPY {lt.api_name} FROM duckdb.{ds.source_identifier} "
                            f"(FROM {from_col} TO {to_col}{props_clause});"
                        )
                        logger.info(f"    - Executando: {cypher}")
                        try:
                            self.kuzu.execute(cypher)
                            # Tentar contar linhas via DuckDB
                            rel_count = 0
                            try:
                                if self.duckdb and ds.source_type == "duckdb_table":
                                    q = f"SELECT COUNT(*) FROM {ds.source_identifier}"
                                    rel_count = int(self.duckdb.execute(q).fetchone()[0])  # type: ignore[attr-defined]
                            except Exception as e:
                                logger.warning(
                                    f"    - Aviso: não foi possível contar linhas para '{lt.api_name}': {e}"
                                )
                            self.metrics.add_rels(lt.api_name, int(rel_count))
                        except Exception as e:
                            logger.error(f"    - ❌ Falha ao carregar relação '{lt.api_name}': {e}")
                            self.metrics.add_warning(f"Falha ao COPY rel '{lt.api_name}': {e}")
                        continue
                    # Se a flag de COPY não estiver ativa, seguir para o fallback abaixo usando leitura
                    ds_desc = ds.api_name or ds.source_identifier
                    raw_df = self._read_dataset(ds)
                    if raw_df is None:
                        self.metrics.add_warning(f"Dataset '{ds_desc}' não pode ser lido; pulando")
                        continue
                    # Incremental APPEND filter if configured on LinkType
                    try:
                        incr_field = getattr(lt, "incremental_field", None)
                        last_sync = getattr(lt, "last_rels_sync_time", None)
                        if (
                            incr_field
                            and last_sync
                            and POLARS_AVAILABLE
                            and incr_field in getattr(raw_df, "columns", [])
                        ):
                            try:
                                ts = last_sync
                                raw_df = raw_df.filter(pl.col(incr_field) > pl.lit(ts))
                            except Exception as e:
                                self.metrics.add_warning(
                                    f"Falha no filtro incremental de relações para '{lt.api_name}': {e}"
                                )
                    except Exception:
                        pass
                    props_clause = ""
                    link_props = getattr(lt, "property_mappings", None) or {}
                    if link_props:
                        props_mapping_str = ", ".join([f"{k} = {v}" for k, v in link_props.items()])
                        props_clause = f", PROPERTIES ({props_mapping_str})"
                    cmd = (
                        f"-- loading rels for {lt.api_name} from dataset {ds_desc} "
                        f"(from_col={from_col}, to_col={to_col}{props_clause})"
                    )
                    self.kuzu.execute(cmd)
                    try:
                        row_count = len(raw_df) if hasattr(raw_df, "__len__") else 0
                        self.metrics.add_rels(lt.api_name, int(row_count))
                    except Exception:
                        self.metrics.add_rels(lt.api_name, 0)
                    # Update last_rels_sync_time
                    try:
                        lt.last_rels_sync_time = datetime.now()
                        self.meta_db.add(lt)
                        self.meta_db.commit()
                    except Exception:
                        pass
                    continue

                # Caminho 2: Fallback por convenção {linkType}_rels
                ds_name = f"{lt.api_name}_rels"
                ds = self.meta_db.exec(select(Dataset).where(Dataset.api_name == ds_name)).first()
                ds_desc = ds_name if not ds else (ds.api_name or ds.source_identifier)
                if not ds:
                    self.metrics.add_warning(
                        f"Dataset de relações não encontrado para '{lt.api_name}'"
                    )
                    continue
                from_col = getattr(lt, "from_property_mapping", None) or f"from_{from_pk}"
                to_col = getattr(lt, "to_property_mapping", None) or f"to_{to_pk}"
                raw_df = self._read_dataset(ds)
                if raw_df is None:
                    self.metrics.add_warning(f"Dataset '{ds_desc}' não pode ser lido; pulando")
                    continue
                # Incremental APPEND filter for conventional dataset
                try:
                    incr_field = getattr(lt, "incremental_field", None)
                    last_sync = getattr(lt, "last_rels_sync_time", None)
                    if (
                        incr_field
                        and last_sync
                        and POLARS_AVAILABLE
                        and incr_field in getattr(raw_df, "columns", [])
                    ):
                        try:
                            ts = last_sync
                            raw_df = raw_df.filter(pl.col(incr_field) > pl.lit(ts))
                        except Exception as e:
                            self.metrics.add_warning(
                                f"Falha no filtro incremental de relações para '{lt.api_name}': {e}"
                            )
                except Exception:
                    pass
                props_clause = ""
                link_props = getattr(lt, "property_mappings", None) or {}
                if link_props:
                    props_mapping_str = ", ".join([f"{k} = {v}" for k, v in link_props.items()])
                    props_clause = f", PROPERTIES ({props_mapping_str})"
                cmd = (
                    f"-- loading rels for {lt.api_name} from dataset {ds_desc} "
                    f"(from_col={from_col}, to_col={to_col}{props_clause})"
                )
                self.kuzu.execute(cmd)
                # Metrics: usar número de linhas lidas
                try:
                    row_count = len(raw_df) if hasattr(raw_df, "__len__") else 0
                    self.metrics.add_rels(lt.api_name, int(row_count))
                except Exception:
                    self.metrics.add_rels(lt.api_name, 0)
                # Update last sync time for relations
                try:
                    lt.last_rels_sync_time = datetime.now()
                    self.meta_db.add(lt)
                    self.meta_db.commit()
                except Exception:
                    pass
            except Exception as e:
                warn = f"Erro ao processar relações para '{lt.api_name}': {e}"
                logger.warning(warn)
                self.metrics.add_warning(warn)


# Criar um __init__.py para o módulo application
__all__ = ["OntologySyncService", "SyncMetrics"]
