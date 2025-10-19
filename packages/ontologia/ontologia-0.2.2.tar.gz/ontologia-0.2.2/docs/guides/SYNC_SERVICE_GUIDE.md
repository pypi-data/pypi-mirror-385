# OntologySyncService - Guia de Implementação
  
  **Data**: 2025-10-02  
  **Status**: ✅ **IMPLEMENTADO**
  
  ---
  
  > Atualização (2025-10-04)
  >
  > - Runner oficial: `scripts/main_sync.py` (o `sync.py` da raiz está depreciado e apenas encaminha para o runner novo).
  > - Carga de relações: ✅ Implementada com suporte a `backing_dataset_rid` e mapeamentos (`fromPropertyMapping`, `toPropertyMapping`, `propertyMappings`). Há caminho otimizado via `COPY` quando `SYNC_ENABLE_COPY_RELS=1`.
  > - Variáveis de ambiente úteis: `KUZU_DB_PATH`, `DUCKDB_PATH`, `SYNC_ENABLE_COPY_RELS`, `SYNC_SETUP`.

  ## 🎯 **O Que É o OntologySyncService?**

  O **OntologySyncService** é o motor ETL que materializa nosso grafo de conhecimento. Ele conecta três "planos":

  ```
  ┌─────────────────────────────────────┐
  │   PLANO DE CONTROLE                 │
  │   (Metadados - SQLModel)            │
  │   - ObjectType                      │
  │   - LinkType                        │
  │   - Dataset                         │
  │   - ObjectTypeDataSource            │
  └─────────────────────────────────────┘
                ↓ (lê metadados)
  ┌─────────────────────────────────────┐
  │   ONTOLOGY SYNC SERVICE             │
  │   (Motor ETL)                       │
  │   - Extrai                          │
  │   - Transforma                      │
  │   - Carrega                         │
  └─────────────────────────────────────┘
                ↓ (extrai dados)
  ┌─────────────────────────────────────┐
  │   PLANO DE DADOS BRUTOS             │
  │   (DuckDB / Parquet)                │
  │   - Tabelas                          │
  │   - Arquivos                         │
  └─────────────────────────────────────┘
                ↓ (carrega grafo)
  ┌─────────────────────────────────────┐
  │   PLANO SEMÂNTICO                   │
  │   (KùzuDB - Grafo)                  │
  │   - Nós (ObjectType instances)      │
  │   - Arestas (LinkType instances)    │
  └─────────────────────────────────────┘
  ```

---

## 🏗️ **Arquitetura**

### **Analogia: Chef de Cozinha**

- **Plano de Controle** = Livro de Receitas  
  - `ObjectType` = Receita do "Bolo de Chocolate"
  
- **Plano de Dados Brutos** = Ingredientes na Despensa  
  - Farinha, ovos, açúcar (dados brutos)
  
- **OntologySyncService** = Chef  
  - Lê a receita
  - Pega os ingredientes
  - Mistura e assa
  
- **Plano Semântico** = Bolo Pronto  
  - Pronto para servir (consultar)

---

## 📊 **Fluxo de Sincronização**

### **Método Principal: `sync_ontology()`**

```python
service = OntologySyncService(
    metadata_session=session,
    kuzu_conn=kuzu_conn,
    duckdb_conn=duckdb_conn
)

metrics = service.sync_ontology(duckdb_path='analytics.duckdb')
```

### **Passos Executados**

#### **1. Construção do Esquema (_build_graph_schema)**
```
Para cada ObjectType:
  ├─ Lê propriedades (PropertyType)
  ├─ Mapeia tipos de dados → KùzuDB
  └─ Executa: CREATE NODE TABLE customer (id STRING, name STRING, PRIMARY KEY (id))

Para cada LinkType:
  ├─ Identifica from_object_type e to_object_type
  └─ Executa: CREATE REL TABLE placesOrder (FROM customer TO order)
```

#### **2. Anexação do DuckDB (_attach_duckdb)**
```
Executa: ATTACH 'analytics.duckdb' AS duckdb (dbtype 'duckdb')
Permite: COPY direto do DuckDB → KùzuDB
```

#### **3. Carga dos Nós (_load_nodes_into_graph)**
```
Para cada ObjectType:
  ├─ Encontra ObjectTypeDataSource links
  ├─ Para cada Dataset:
  │   ├─ Lê dados (Polars)
  │   │   ├─ source_type = 'duckdb_table' → pl.read_database()
  │   │   └─ source_type = 'parquet_file' → pl.read_parquet()
  │   ├─ Aplica property_mappings (renomeia colunas)
  │   └─ Adiciona ao pool de união
  ├─ Une (UNION) todos os DataFrames
  ├─ Remove duplicatas (pela primary_key)
  └─ Carrega em lote: kuzu_conn.load_from_polars(df, 'customer')
```

#### **4. Carga das Relações (_load_rels_into_graph)**
```
Para cada LinkType:
  ├─ Encontra backing_dataset (dataset de junção)
  ├─ Usa from_property_mapping e to_property_mapping
  └─ Executa: COPY placesOrder FROM duckdb.customer_orders (FROM customer_id TO order_id)
```

---

## 💡 **Recursos Implementados**

### **1. SyncMetrics - Monitoramento**
```python
metrics = service.sync_ontology()

print(metrics.summary())
# ============================================================
# SYNC METRICS SUMMARY
# ============================================================
# Duration: 2.45s
# Nodes Created: 150
#   - customer: 100
#   - order: 50
# Relations Created: 75
#   - placesOrder: 75
# Warnings: 0
# Errors: 0
# ============================================================
```

### **2. Mapeamento de Tipos**
```python
type_mapping = {
    'string': 'STRING',
    'integer': 'INT64',
    'double': 'DOUBLE',
    'boolean': 'BOOL',
    'date': 'DATE',
    'timestamp': 'TIMESTAMP',
}
```

### **3. Múltiplas Fontes (Federation)**
```python
# ObjectType pode ter múltiplos Datasets
customer.data_sources → [
    Dataset('customer_main.parquet'),
    Dataset('customer_updates.parquet'),
    Dataset('customer_legacy_table')
]

# Serviço une todos automaticamente
# e remove duplicatas pela primary_key
```

### **4. Tratamento de Erros**
- Erros individuais não param o processo completo
- Cada erro é registrado em `metrics.errors`
- Warnings para fontes não processáveis

---

## 🚀 **Como Usar**

### **Instalação de Dependências**
```bash
# Dependências principais (já instaladas)
pip install sqlmodel pydantic registro

# Dependências do sync service (opcionais)
pip install kuzu duckdb polars
```

### **Exemplo Completo (scripts/main_sync.py)**
```python
from ontologia.application import OntologySyncService
import kuzu
import duckdb
from sqlmodel import Session

# 1. Setup dos bancos
metadata_engine = create_engine("sqlite:///metadata.db")
duckdb_conn = duckdb.connect('analytics.duckdb')
kuzu_conn = kuzu.Connection(kuzu.Database('graph_db'))

# 2. Popular Plano de Controle
with Session(metadata_engine) as session:
    setup_control_plane(session)  # Criar ObjectTypes, Datasets, etc.

# 3. Criar dados brutos no DuckDB
create_sample_data(duckdb_conn)

# 4. Sincronizar!
with Session(metadata_engine) as session:
    service = OntologySyncService(session, kuzu_conn, duckdb_conn)
    metrics = service.sync_ontology(duckdb_path='analytics.duckdb')

# 5. Consultar o grafo
result = kuzu_conn.execute("MATCH (c:customer) RETURN c.name, c.age;")
print(result.get_as_df())
```

### **Executar o Exemplo**
```bash
# Executar o runner oficial
python scripts/main_sync.py

# Saída esperada:
# ============================================================
# ONTOLOGY SYNC SERVICE - EXEMPLO COMPLETO
# ============================================================
# 📦 Inicializando banco de metadados...
# ✅ Banco de metadados criado
# 📋 Populando Plano de Controle...
# ...
# ✅ EXEMPLO COMPLETO EXECUTADO COM SUCESSO!
```

---

## 📁 **Arquivos Criados**

### **Código Principal**
- ✅ `ontologia/application/sync_service.py` - OntologySyncService
- ✅ `ontologia/application/__init__.py` - Exports

  ### **Exemplos**
  - ✅ `sync.py` - Exemplo end-to-end completo

  ### **Testes**
  - ✅ `test_sync_service.py` - Testes unitários

### **Documentação**
- ✅ `SYNC_SERVICE_GUIDE.md` - Este guia

---
{{ ... }}

## 🧪 **Testes**

### **Rodar Testes Unitários**
```bash
pytest test_sync_service.py -v
```

### **Testes Incluídos**
- ✅ `test_sync_metrics` - Tracking de métricas
- ✅ `test_sync_service_imports` - Imports funcionando
- ✅ `test_sync_service_initialization` - Inicialização
- ✅ `test_control_plane_setup` - Setup do plano de controle
- ✅ `test_type_mapping` - Mapeamento de tipos

---

## 🎯 **Recursos Avançados (Futuro)**

### **1. Incremental Sync**
```python
# Usar TransactionType para determinar estratégia
if transaction.transaction_type == TransactionType.SNAPSHOT:
    # Substituir todos os dados
    truncate_and_load()
elif transaction.transaction_type == TransactionType.APPEND:
    # Apenas adicionar novos
    append_only()
```

### **2. Propriedades em Relacionamentos**
```python
# LinkType com propriedades
CREATE REL TABLE placesOrder (
    FROM customer TO order,
    order_date TIMESTAMP,
    status STRING
)
```

### **3. Scheduling & Automação**
```python
# Agendar sync periódico
import schedule

def sync_job():
    with Session(engine) as session:
        service = OntologySyncService(session, kuzu_conn, duckdb_conn)
        service.sync_ontology()

schedule.every().hour.do(sync_job)
```

### **4. Delta Detection**
```python
# Detectar apenas mudanças desde última sync
def sync_delta(since: datetime):
    # Ler apenas registros modificados após 'since'
    # Aplicar apenas essas mudanças no grafo
    pass
```

---

## 📊 **Exemplos de Queries no Grafo**

### **Query 1: Todos os Clientes**
```cypher
MATCH (c:customer)
RETURN c.customer_id, c.name, c.email
ORDER BY c.name;
```

### **Query 2: Pedidos por Cliente**
```cypher
MATCH (c:customer)-[:placesOrder]->(o:order)
RETURN c.name, COUNT(o) as order_count, SUM(o.total) as total_spent
ORDER BY total_spent DESC;
```

### **Query 3: Clientes sem Pedidos**
```cypher
MATCH (c:customer)
WHERE NOT EXISTS {
    MATCH (c)-[:placesOrder]->()
}
RETURN c.name, c.email;
```

### **Query 4: Pedidos Recentes**
```cypher
MATCH (c:customer)-[:placesOrder]->(o:order)
WHERE o.order_date > timestamp('2024-01-25')
RETURN c.name, o.order_id, o.total, o.order_date
ORDER BY o.order_date DESC;
```

---

## 🔧 **Configuração Recomendada**

### **Estrutura de Projeto**
```
 /ontologia/
 ├── metadata.db           # Plano de Controle (SQLite)
 ├── analytics.duckdb      # Plano de Dados Brutos (DuckDB)
 ├── graph_db/             # Plano Semântico (KùzuDB)
 │
 ├── scripts/
 │   └── main_sync.py      # Runner oficial de sincronização
 │
 ├── ontologia/
 │   ├── application/
 │   │   ├── __init__.py
 │   │   └── sync_service.py  # ← Serviço
 │   │
 │   └── domain/
 │       └── metamodels/
 │           └── instances/
 │               └── dtos.py  # DTOs de instância (Pydantic)
 │
 └── datacatalog/
     └── models.py
```

### **Workflow Recomendado**
```
1. Design → Criar ObjectTypes, LinkTypes (main_with_datacatalog.py)
2. Data → Criar/popular Datasets no DuckDB
3. Link → Criar ObjectTypeDataSource (conectar ObjectType → Dataset)
4. Sync → Executar OntologySyncService
5. Query → Consultar grafo no KùzuDB
6. Iterate → Refinar modelo e repetir
```

---

## ⚠️ **Limitações Atuais**

### **1. LinkType Relations**
- Carga de relações requer `backing_dataset_rid` em LinkType
- Ainda não implementado (TODO)
- Workaround: criar relações manualmente via Cypher

### **2. Source Types**
- Suportados: `duckdb_table`, `parquet_file`
- Não suportados ainda: `postgres`, `mysql`, `csv`

### **3. Schema Evolution**
- Mudanças no schema do ObjectType não são detectadas automaticamente
- Requer drop/recreate do grafo

### **4. Transações**
- Não há suporte transacional (all-or-nothing)
- Erros em parte dos dados não revertem o resto

---

## 📈 **Métricas de Performance**

### **Benchmarks (estimados)**

| Operação | Tamanho | Tempo | Throughput |
|----------|---------|-------|------------|
| CREATE NODE TABLE | 1 tabela | ~10ms | - |
| LOAD NODES | 10K rows | ~500ms | 20K rows/s |
| LOAD NODES | 100K rows | ~3s | 33K rows/s |
| LOAD NODES | 1M rows | ~25s | 40K rows/s |

---

## ✅ **Status de Implementação**

| Funcionalidade | Status | Detalhes |
|----------------|--------|----------|
| **Schema Building** | ✅ COMPLETO | NODE TABLE, REL TABLE |
| **DuckDB Attach** | ✅ COMPLETO | Anexação automática |
| **Node Loading** | ✅ COMPLETO | Union, dedup, bulk load |
| **Relation Loading** | ✅ COMPLETO | COPY via DuckDB opcional; fallback suportado |
| **Metrics** | ✅ COMPLETO | Tracking completo |
| **Error Handling** | ✅ COMPLETO | Graceful degradation |
| **Type Mapping** | ✅ COMPLETO | Todos tipos básicos |
| **Multiple Sources** | ✅ COMPLETO | Federation funcional |
| **Parquet Support** | ✅ COMPLETO | Via Polars |
| **DuckDB Support** | ✅ COMPLETO | Via Polars |

---

## 🧭 **Modo de Grafo Unificado (padrão obrigatório)**

O projeto usa um modelo de grafo unificado obrigatório, onde todas as instâncias são armazenadas em uma única `NODE TABLE Object`. Esse modo elimina `UNION` em consultas de Interface e utiliza múltiplos rótulos (labels) por nó.

### O que muda

- **Schema (KùzuDB) – criado pelo SyncService:**
  - `Object(rid STRING PRIMARY KEY, objectTypeApiName STRING, pkValue STRING, labels STRING[], properties STRING)`
  - Relações: `CREATE REL TABLE <LinkTypeApiName> (FROM Object TO Object)`
- **Identificador estável (`rid`):** `"{service}:{instance}:{objectTypeApiName}:{pk}"`
- **Propriedades:** armazenadas como JSON em `properties`.
- **Labels:** incluem o ObjectType concreto e as Interfaces implementadas.

### Leitura (API / Repositórios)

- `GraphInstancesRepository` usa `MATCH (o:Object)` e filtra por `objectTypeApiName`, `pkValue` e `labels`.
- `list_by_interface()` filtra via `'<interface>' IN o.labels` (sem `UNION`).
- `get_linked_objects()` faz traversal `Object → Object` pelas `REL TABLEs` dos `LinkTypes`.
- `AnalyticsService` (quando disponível grafo): lista do `Object` e agrega em memória a partir de `properties` (JSON). Mantém path legado quando flag desativada.

### Como garantir

1. Verifique `ontologia.toml` (valor padrão já é `true`):

   ```toml
   [features]
   use_unified_graph = true
   ```

2. (Opcional) exporte `KUZU_DB_PATH` para apontar para o diretório desejado.

> Observação: tentativas de desabilitar com `USE_UNIFIED_GRAPH=0` são ignoradas; o `OntologySyncService._build_graph_schema()` é sempre a fonte da verdade.

### Migração / Reset

1. Pare a API e garanta que nenhum processo esteja usando o Kùzu.
2. Limpe (ou aponte para outro diretório) o DB do Kùzu. Você pode usar o comando

```bash
ontologia graph reset --yes
```

   ou remover manualmente o diretório: `rm -rf ${KUZU_DB_PATH:-instance_graph.kuzu}`.

3. Certifique-se de que `use_unified_graph` permaneça `true` no manifest (o padrão) e, se necessário, defina `KUZU_DB_PATH`.
4. Execute o `OntologySyncService` novamente para reconstruir o schema unificado e recarregar nós e relações.
5. Valide consultas de Interface (sem `UNION`) e traversal `Object→Object` pelas rotas v2.

### Compatibilidade

- O grafo unificado é o único modo suportado. Caso o Kùzu não esteja disponível, os repositórios retornam ao SQLModel.

---

## 🚀 **Próximos Passos**

### **Para a Equipe de Desenvolvimento**

1. **Implementar Backing Dataset em LinkType**
   - Adicionar `backing_dataset_rid` campo
   - Adicionar `from_property_mapping`, `to_property_mapping`
   - Completar `_load_rels_into_graph()`

2. **Adicionar Mais Source Types**
   - PostgreSQL
   - MySQL
   - CSV files
   - REST APIs

3. **Implementar Incremental Sync**
   - Usar `TransactionType` (SNAPSHOT vs APPEND)
   - Delta detection
   - Upsert logic

4. **Schema Evolution**
   - Detectar mudanças no ObjectType
   - Migrar dados automaticamente
   - ALTER TABLE support

5. **Transações & Rollback**
   - Atomic operations
   - Checkpoints
   - Recovery on failure

---

## 📚 **Referências**

- **KùzuDB Docs**: https://kuzudb.com/docs
- **DuckDB Docs**: https://duckdb.org/docs
- **Polars Docs**: https://pola-rs.github.io/polars/
- **Palantir Foundry**: Inspiração para o padrão Dataset/Transaction/Branch

---

## 🎉 **Conclusão**

O **OntologySyncService** está **implementado e funcional**!

**O que funciona:**
- ✅ Leitura de metadados do Plano de Controle
- ✅ Construção automática do esquema do grafo
- ✅ Extração de dados do DuckDB/Parquet
- ✅ União de múltiplas fontes (federation)
- ✅ Remoção de duplicatas
- ✅ Bulk load otimizado no KùzuDB
- ✅ Tracking completo de métricas
- ✅ Error handling robusto

**Para usar:**
```bash
# 1. Instalar dependências
pip install kuzu duckdb polars

# 2. Executar exemplo
python sync.py

# 3. Consultar o grafo!
```

**A plataforma agora tem um motor ETL completo que materializa
o conhecimento do Plano de Controle em um grafo consultável!** 🚀

---

**Implementado por**: Sistema de IA  
**Data**: 2025-10-02  
**Versão**: 1.0.0
