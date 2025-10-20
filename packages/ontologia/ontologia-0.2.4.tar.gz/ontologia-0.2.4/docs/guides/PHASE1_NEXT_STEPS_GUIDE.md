# 📘 Guia de Implementação Detalhado – Fase 1: Próximos Passos

Data: 2025-10-03  
Autor: Arquiteto do Projeto  
Público: Equipe de Desenvolvimento

---

## 🧭 Missão

Construir uma alternativa OSS à ontologia do Palantir Foundry. Além do código, a clareza da arquitetura e a robustez da implementação são os nossos maiores diferenciais.

Este guia detalha os próximos passos para refinarmos a Fase 1, com foco em: separação de responsabilidades, reconciliação de propriedades, paridade de funcionalidades para `LinkType`, e cultura de testes.

---

## 🗂️ Estrutura atual relevante (arquivos)

- `api/repositories/metamodel_repository.py`
- `api/services/metamodel_service.py`
- `api/v2/schemas/metamodel.py`
- `api/v2/routers/object_types.py`
- `api/v2/routers/link_types.py`
- `ontologia/domain/metamodels/types/object_type.py`
- `ontologia/domain/metamodels/types/property_type.py`
- `ontologia/domain/metamodels/types/link_type.py`
- `test_api.py` (testes de API)

---

## ✅ Resultado atual (baseline)

- API v2 funcional (ObjectTypes e LinkTypes) com FastAPI.
- Multi-tenant por `service`/`instance` (alinhado com Registro), com busca via `JOIN` em `registro.core.resource.Resource`.
- Routers corrigidos para usar `ontologyApiName` e criar `MetamodelService(session, service="ontology", instance=ontologyApiName)`.
- Testes de API passando (13/13) com validações.
- Avisos eliminados (Pydantic v2, SQLAlchemy session warnings):
  - `min_items → min_length`
  - Evitar atribuir relacionamentos fora de sessão (setar apenas FKs e deixar o ORM carregar)

---

## Tarefa 1: Refinar a Lógica de Upsert (Criação/Atualização)

### Filosofia (O Porquê)
A camada de Serviço deve conter toda a lógica de negócio (incluindo decidir entre criar ou atualizar). O Repositório deve ser simples, focado em operações de persistência. Isso reforça o Princípio da Responsabilidade Única, melhora testabilidade e clareza.

### Plano de Ação (O Como)

- **Simplifique o Repositório**: remova o `if existing` de `save_*`. O repositório só faz `add/commit/refresh`.

Arquivo: `api/repositories/metamodel_repository.py`
```python
# ... outros métodos ...

class MetamodelRepository:
    # ...
    def save_object_type(self, object_type: ObjectType) -> ObjectType:
        """
        Persiste um ObjectType (insert ou update).
        A decisão de criação/atualização já foi tomada na camada de serviço.
        """
        self.session.add(object_type)
        self.session.commit()
        self.session.refresh(object_type)
        return object_type

    def save_link_type(self, link_type: LinkType) -> LinkType:
        self.session.add(link_type)
        self.session.commit()
        self.session.refresh(link_type)
        return link_type
```

- **Mova a lógica para o Serviço**: `MetamodelService.upsert_object_type()` e `upsert_link_type()` fazem: buscar existente → decidir criar/atualizar → setar campos → persistir.

Arquivo: `api/services/metamodel_service.py`
```python
class MetamodelService:
    def upsert_object_type(self, api_name: str, schema: ObjectTypePutRequest) -> ObjectTypeReadResponse:
        # Buscar existente
        existing = self.repo.get_object_type_by_api_name(self.service, self.instance, api_name)

        if existing:
            # Atualização
            print(f"INFO: Atualizando ObjectType existente: {api_name}")
            obj = existing
            obj.display_name = schema.displayName
            obj.description = schema.description
            obj.primary_key_field = schema.primaryKey
        else:
            # Criação
            print(f"INFO: Criando novo ObjectType: {api_name}")
            obj = ObjectType(
                service=self.service,
                instance=self.instance,
                api_name=api_name,
                display_name=schema.displayName,
                description=schema.description,
                primary_key_field=schema.primaryKey,
            )

        # Tarefa 2: reconciliação de propriedades (abaixo)
        # ...

        saved = self.repo.save_object_type(obj)
        return self._object_type_to_response(saved)
```

> Observações de implementação:
> - Use transações finas quando necessário (e.g., flush antes de reconciliação) para garantir `rid` no pai.
> - Evite atribuir relacionamentos diretamente fora da sessão; prefira setar FKs e deixar o ORM carregar.

---

## Tarefa 2: Conversão DTO → Modelo de Domínio (com Propriedades)

### Filosofia (O Porquê)
A API recebe `ObjectTypePutRequest` (DTO), mas persistimos `ObjectType` + `PropertyType` (modelos de domínio). A camada de Serviço deve reconciliar o estado: adicionar novas propriedades, remover antigas e atualizar existentes. PUT significa substituir totalmente a configuração.

### Plano de Ação (O Como)

Arquivo: `api/services/metamodel_service.py` (continuação do método `upsert_object_type`)
```python
# Depois de decidir obj (novo ou existente):
# 1) Mapear estado atual (DB) e alvo (DTO)
current_props = {p.api_name: p for p in obj.property_types}
schema_props = {k: v for k, v in schema.properties.items()}

current_names = set(current_props.keys())
schema_names = set(schema_props.keys())

# 2) Remover ausentes
for name in current_names - schema_names:
    print(f"INFO: Deletando propriedade: {name}")
    self.session.delete(current_props[name])

# 3) Adicionar/Atualizar presentes
for name in schema_names:
    pd = schema_props[name]
    is_pk = name == schema.primaryKey

    if name in current_props:
        prop = current_props[name]
        print(f"INFO: Atualizando propriedade: {name}")
        prop.display_name = pd.displayName
        prop.description = pd.description
        prop.data_type = pd.dataType
        prop.required = (pd.required or False) or is_pk
        prop.is_primary_key = is_pk
    else:
        print(f"INFO: Adicionando propriedade: {name}")
        new_prop = PropertyType(
            service=self.service,
            instance=self.instance,
            api_name=name,
            display_name=pd.displayName,
            description=pd.description,
            data_type=pd.dataType,
            required=(pd.required or False) or is_pk,
            is_primary_key=is_pk,
            object_type_rid=obj.rid,
            object_type_api_name=obj.api_name,
        )
        self.session.add(new_prop)

# 4) Persistir
saved = self.repo.save_object_type(obj)
return self._object_type_to_response(saved)
```

> Boas práticas:
> - Garanta que a propriedade `primaryKey` exista em `properties` e seja `required=True` (validação já implementada).
> - Evite atribuir `obj.property_types.append(...)` diretamente fora de sessão (previne SAWarnings). Use FKs e `session.add`.
> - Considere usar `session.flush()` após criar o pai para garantir `rid` antes de criar filhos.

---

## Tarefa 3: Completar Métodos para LinkType

### Filosofia (O Porquê)
Paridade de funcionalidades com `ObjectType`. Validações de negócio (existência de `fromObjectType` e `toObjectType`) acontecem na camada de Serviço. Repositório permanece simples.

### Plano de Ação (O Como)

- **Repositório**: métodos `get_link_type_by_api_name()`, `save_link_type()`, `list_link_types()`, `delete_link_type()` (já existem e usam `JOIN` com `Resource`).
- **Serviço**: `upsert_link_type()` com validações e conversão DTO → modelo.

Arquivo: `api/services/metamodel_service.py`
```python
def upsert_link_type(self, api_name: str, schema: LinkTypePutRequest) -> LinkTypeReadResponse:
    # 1) Validar existência dos ObjectTypes
    from_ot = self.repo.get_object_type_by_api_name(self.service, self.instance, schema.fromObjectType)
    if not from_ot:
        raise HTTPException(status_code=400, detail=f"ObjectType '{schema.fromObjectType}' not found")

    to_ot = self.repo.get_object_type_by_api_name(self.service, self.instance, schema.toObjectType)
    if not to_ot:
        raise HTTPException(status_code=400, detail=f"ObjectType '{schema.toObjectType}' not found")

    # 2) Buscar existente
    existing = self.repo.get_link_type_by_api_name(self.service, self.instance, api_name)

    cardinality = Cardinality(schema.cardinality)

    if existing:
        lt = existing
        lt.display_name = schema.displayName
        lt.inverse_api_name = schema.inverse.apiName
        lt.inverse_display_name = schema.inverse.displayName
        lt.cardinality = cardinality
        lt.from_object_type_api_name = schema.fromObjectType
        lt.to_object_type_api_name = schema.toObjectType
    else:
        lt = LinkType(
            service=self.service,
            instance=self.instance,
            api_name=api_name,
            display_name=schema.displayName,
            inverse_api_name=schema.inverse.apiName,
            inverse_display_name=schema.inverse.displayName,
            cardinality=cardinality,
            from_object_type_api_name=schema.fromObjectType,
            to_object_type_api_name=schema.toObjectType,
        )

    # 3) Resolver RIDs e validar PKs dos ObjectTypes
    lt.validate_and_resolve_object_types(self.session)

    # 4) Persistir
    saved = self.repo.save_link_type(lt)
    return self._link_type_to_response(saved)
```

> Nota: Nosso modelo `LinkType` não tem `description`; o DTO de resposta usa `getattr(link_type, "description", None)` para compatibilidade com cliente.

---

## Tarefa 4: Estruturar e Implementar Testes

### Filosofia (O Porquê)
Sem testes, não há segurança para evoluir. Vamos combinar testes unitários (lógica isolada) e de integração (fluxo completo via HTTP API).

### Plano de Ação (O Como)

- **Diretórios**
  - `tests/unit/` – foca em `MetamodelService` com repositório mockado.
  - `tests/integration/` – usa `TestClient` do FastAPI com SQLite em memória.

- **Testes Unitários**
Arquivo: `tests/unit/test_metamodel_service.py`
```python
from unittest.mock import MagicMock
import pytest
from fastapi import HTTPException
from api.services.metamodel_service import MetamodelService
from api.v2.schemas.metamodel import ObjectTypePutRequest, PropertyDefinition

def test_upsert_object_type_validates_primary_key():
    mock_session = MagicMock()
    mock_repo = MagicMock()

    service = MetamodelService(session=mock_session)
    service.repo = mock_repo  # injeta mock

    invalid_schema = ObjectTypePutRequest(
        displayName="Test",
        primaryKey="id",
        properties={"name": PropertyDefinition(dataType="string", displayName="Name")}
    )

    with pytest.raises(HTTPException) as exc:
        service.upsert_object_type("TestType", invalid_schema)

    assert exc.value.status_code == 400
    assert "must be defined in properties" in exc.value.detail
```

- **Testes de Integração**
Arquivo: `tests/integration/test_api_v2_object_types.py`
```python
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_create_object_type_success():
    response = client.put(
        "/v2/ontologies/default/objectTypes/Funcionario",
        json={
            "displayName": "Funcionário",
            "primaryKey": "employeeId",
            "properties": {
                "employeeId": {"dataType": "string", "displayName": "ID", "required": True}
            }
        }
    )
    assert response.status_code in (200, 201)
    data = response.json()
    assert data["apiName"] == "Funcionario"
    assert data["primaryKey"] == "employeeId"
```

> Dicas:
> - Use `StaticPool` e `sqlite:///:memory:` com `dependency_overrides` para isolar o DB por teste.
> - Gere cenários para validações negativas (ex.: `primaryKey` ausente, `required=False` na PK, `LinkType` com ObjectTypes inexistentes).

---

## Critérios de Aceite (Definition of Done)

- **Upsert**: Lógica de decisão exclusivamente na camada de Serviço (Repositório sem `if existing`).
- **Reconciliação**: PUT de `ObjectType` substitui completamente o conjunto de propriedades.
- **LinkType**: CRUD com validação de existência dos ObjectTypes relacionados.
- **Multi-tenancy**: Todas as consultas por `service/instance` via `JOIN` com `Resource`.
- **Qualidade**: Testes unitários e de integração cobrindo casos de sucesso e erro.
- **Documentação**: Este guia + `API_PHASE1_GUIDE.md` atualizados.

---

## Boas Práticas & Observações

- **Transações**: use `session.flush()` para garantir `rid` antes de criar filhos; comite atomicamente quando possível.
- **Relacionamentos**: prefira setar FKs e evitar `append` direto fora da sessão (evita SAWarnings). Deixe o ORM carregar as coleções.
- **Validações**: mantenha regras de negócio na camada de Serviço; o Repositório não valida domínio.
- **OpenAPI**: mantenha `schemas` e descrições atualizadas; continue compatível com Foundry.
- **Logs**: mensagens `INFO:` nos caminhos principais (`criação`, `atualização`, `reconciliação`).

---

## Próximos Passos (Fase 2 – Visão)

1. **Motor de Query Híbrido**: SQL (metadados) + Cypher (grafos) com endpoints de consulta.
2. **Instances API**: CRUD de `Object` e `LinkedObject` (camada semântica no KùzuDB).
3. **AuthZ/AuthN**: JWT + RBAC + escopo por `service/instance`.
4. **Performance**: Caching (Redis), pooling e otimizações de consultas.

---

## Referências

- Foundry Ontology API – v2
- Padrões: Repository, Service Layer, SRP, DTO ↔ Domain
- Pydantic v2 Migração – evitar `min_items` (usar `min_length`)

---

Se houver dúvidas ou ajustes desejados, atualizaremos este guia e abriremos tarefas correspondentes no backlog. Vamos em frente! 🚀
