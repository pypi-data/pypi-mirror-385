# Análise do Palantir Foundry SDK e Recomendações para Ontologia

**Data**: 2025-10-01  
**Objetivo**: Entender como o Foundry lida com Link Types bidirecionais e aplicar ao projeto Ontologia

---

## 1. 🔍 Como o Palantir Foundry Lida com Link Types

### Análise do SDK e Documentação

Baseado no código do Foundry SDK e na documentação oficial, o Foundry **NÃO** usa o conceito de "LinkTypeSide" como entidades separadas. Em vez disso, eles tratam links de forma unificada:

### Estrutura de Link no Foundry

```typescript
// Conceitual - baseado na API do Foundry
interface LinkType {
  apiName: string;              // Ex: "worksFor"
  displayName: string;          // Ex: "Trabalha Para"
  
  // Cardinalidade é da relação completa
  cardinality: "ONE_TO_ONE" | "ONE_TO_MANY" | "MANY_TO_ONE" | "MANY_TO_MANY";
  
  // Objetos conectados
  objectTypeA: string;          // Ex: "Employee" 
  objectTypeB: string;          // Ex: "Company"
  
  // Inverso é definido junto
  inverse: {
    apiName: string;            // Ex: "employees"
    displayName: string;        // Ex: "Empregados"
  }
}
```

### Diferenças Chave vs. Implementação Atual

| Aspecto | Ontologia Atual | Foundry |
|---------|-----------------|---------|
| **Estrutura** | `LinkTypeSide` separado | `LinkType` unificado |
| **Cardinalidade** | Em cada "lado" | No link completo |
| **Inverso** | Implícito/separado | Explícito no mesmo objeto |
| **Criação** | Dois registros | Um registro atômico |

---

## 2. 📝 Explicação: `references_object_type_api_name` no PropertyType

### O Problema Atual

No código atual (`link_type.py`), quando você usa uma propriedade como FK, o sistema "adivinha" o tipo de destino:

```python
# Código atual em validate_object_types()
property_type = self._get_foreign_key_property(session)

# ADIVINHAÇÃO baseada em convenção de nomes:
self.target_object_type_api_name = property_type.api_name.replace("_id", "").replace("_rid", "")

# Se property_type.api_name = "address_id"
# Então target = "address"
```

**Problemas com essa abordagem**:
1. ❌ Depende de convenção rígida de nomes (`campo_id` ou `campo_rid`)
2. ❌ Quebra se você nomear diferente (ex: `residencia_fk`, `endereco_principal`)
3. ❌ Não é autodocumentado (precisa ler código para entender a lógica)

### A Solução Proposta

Adicionar um campo **explícito** no `PropertyType` que declara para qual `ObjectType` ele aponta:

```python
# Em property_type.py
class PropertyType(ResourceTypeBaseModel, table=True):
    # ... campos existentes ...
    
    # NOVO CAMPO:
    references_object_type_api_name: Optional[str] = Field(
        default=None,
        description="Se esta propriedade é uma FK, indica o ObjectType que ela referencia"
    )
```

### Como Usar

**Ao definir a propriedade**:
```python
# Em main.py, ao criar propriedades do Person
person_properties = [
    {
        "api_name": "address_id",
        "display_name": "Address ID",
        "data_type": "string",
        "required": False,
        # DECLARAÇÃO EXPLÍCITA:
        "references_object_type_api_name": "address"
    }
]
```

**Ao resolver o link**:
```python
# Em link_type.py::validate_object_types()
property_type = self._get_foreign_key_property(session)

# LÓGICA NOVA (robusta):
if property_type.references_object_type_api_name:
    self.target_object_type_api_name = property_type.references_object_type_api_name
else:
    raise ValueError(
        f"Propriedade '{property_type.api_name}' não define 'references_object_type_api_name'. "
        "Não é possível resolver o tipo de objeto de destino."
    )
```

### Vantagens

| Aspecto | Antes | Depois |
|---------|-------|--------|
| **Flexibilidade** | Apenas `*_id` ou `*_rid` | Qualquer nome |
| **Clareza** | Implícito | Explícito |
| **Validação** | Impossível | Pode validar se ObjectType existe |
| **Docs** | Precisa ler código | Autodocumentado |

### Exemplo Prático

```python
# ANTES: Só funciona com convenção rígida
{
    "api_name": "address_id",  # ✅ Funciona (remove "_id" = "address")
}

{
    "api_name": "local_de_moradia",  # ❌ Quebra (remove o quê?)
}

# DEPOIS: Funciona com qualquer nome
{
    "api_name": "address_id",
    "references_object_type_api_name": "address"  # ✅ Explícito
}

{
    "api_name": "local_de_moradia",
    "references_object_type_api_name": "address"  # ✅ Explícito
}
```

---

## 3. ✅ Conformidade com o Briefing Inicial

### Mapeamento Briefing → Implementação

#### ✅ **I. Camada Núcleo (Core Layer)** - IMPLEMENTADO

| Briefing | Implementação | Status |
|----------|---------------|--------|
| Conceito de `Resource` universal | `registro.core.Resource` | ✅ 100% |
| Identificação única (RID) | `registro.models.RID` | ✅ 100% |
| Todas as coisas são Resources | Herança de `ResourceTypeBaseModel` | ✅ 100% |

**Comentário**: A Camada Núcleo está **perfeitamente implementada** através do projeto `registro`.

---

#### ✅ **II. Camada de Metamodelo (Metamodel Layer)** - IMPLEMENTADO

| Conceito do Briefing | Implementação | Status | Notas |
|----------------------|---------------|--------|-------|
| **`DataType`** | `property_data_type.py` | ✅ 100% | String, Integer, Array, Struct, etc. |
| **`Property`** | `PropertyType` | ✅ 100% | Nome + DataType + validações |
| **`ObjectType`** | `ObjectType` | ✅ 100% | Lista de PropertyTypes + PrimaryKey |
| **`LinkType`** | `LinkTypeSide` | ⚠️ 80% | Parcialmente - falta inverso explícito |

**Detalhes sobre LinkType**:

**O que está implementado** ✅:
- ✅ Define relação entre `SourceObjectType` e `TargetObjectType`
- ✅ Tem cardinalidade (`ONE`, `MANY`)
- ✅ Pode ter propriedades próprias (via lista de Properties)
- ✅ Usa PrimaryKeys dos objetos para estabelecer conexão

**O que está parcialmente implementado** ⚠️:
- ⚠️ `LinkTypeSide` representa **um lado** da relação, não a relação completa
- ⚠️ Não há conceito explícito de "inverso" unificado
- ⚠️ Cardinalidade está em cada lado, não na relação como um todo

**Alinhamento com o Briefing**:
> "Define um tipo de relacionamento que pode existir entre um `SourceObjectType` e um `TargetObjectType`"

Atualmente, `LinkTypeSide` define isso, mas de forma **unidirecional**. O briefing implica uma relação **bidirecional** única.

---

#### ❌ **III. Camada de Dados (Data Layer)** - NÃO IMPLEMENTADO

| Conceito do Briefing | Implementação | Status | Notas |
|----------------------|---------------|--------|-------|
| **`Dataset`** | `/instances/dataset.py` (vazio) | ❌ 0% | Planejado |
| **`Object`** | `/instances/object.py` (vazio) | ❌ 0% | Planejado |
| **`ObjectLink`** | `/instances/object_link.py` (vazio) | ❌ 0% | Planejado |

**Comentário**: Esta camada ainda não foi implementada, mas está **prevista** (arquivos placeholder existem).

---

### Resumo de Conformidade

```
Camada Núcleo:           ████████████████████ 100% ✅
Camada Metamodelo:       ████████████████░░░░  80% ⚠️
Camada de Dados:         ░░░░░░░░░░░░░░░░░░░░   0% ❌

CONFORMIDADE GERAL:      ████████████░░░░░░░░  60% ⚠️
```

### Divergências Específicas

#### 1. LinkType vs LinkTypeSide

**Briefing diz**:
> "Define um tipo de relacionamento... com uma lista de Properties"

**Implementação atual**:
- `LinkTypeSide` define **metade** do relacionamento
- Para ter a relação completa, precisa criar **dois** `LinkTypeSides`

**Recomendação**: Alinhar com Foundry (ver Seção 4).

#### 2. Cardinalidade

**Briefing diz**:
> "A definição de um LinkType... suas instâncias (ObjectLinks) utilizarão as Properties designadas como PrimaryKey"

**Implementação atual**:
- ✅ Correto: usa PrimaryKeys para estabelecer conexão
- ⚠️ Parcial: cardinalidade está em cada "lado", não no link

#### 3. Contextualização por Dataset

**Briefing diz**:
> "Object = ObjectType + Dataset"  
> "ObjectLink = LinkType + Dataset"

**Implementação atual**:
- ❌ Camada de Dados não existe ainda
- ⚠️ Não há conceito de `Dataset` no metamodelo

---

## 4. 🚀 Recomendações para Alinhamento Completo

### Prioridade ALTA: Refatorar LinkType

**Objetivo**: Alinhar com Foundry e com o Briefing.

**Ação**: Substituir `LinkTypeSide` por `LinkType` unificado.

```python
# Novo modelo: link_type.py
class LinkType(ResourceTypeBaseModel, table=True):
    """
    Representa uma relação bidirecional completa entre dois ObjectTypes.
    Alinhado com Palantir Foundry e com o briefing do projeto.
    """
    __resource_type__ = "link-type"
    
    # Cardinalidade da relação completa
    cardinality: Cardinality = Field(...)
    
    # Lado "Forward" (A -> B)
    from_object_type_api_name: str = Field(..., index=True)
    to_object_type_api_name: str = Field(..., index=True)
    
    # Lado "Inverse" (B -> A) - definido explicitamente
    inverse_api_name: str = Field(unique=True, index=True)
    inverse_display_name: str
    
    # Relacionamentos com ObjectTypes
    from_object_type_rid: str = Field(foreign_key="objecttype.rid")
    to_object_type_rid: str = Field(foreign_key="objecttype.rid")
    
    # Propriedades do link (opcional)
    properties: List["PropertyType"] = Relationship(...)
```

**Benefícios**:
- ✅ Alinha com Foundry
- ✅ Alinha com Briefing (relação única, não "lados")
- ✅ Garante consistência bidirecional
- ✅ Simplifica lógica de negócio

---

### Prioridade MÉDIA: Implementar Camada de Dados

**Objetivo**: Completar as 3 camadas do briefing.

**Ação**: Implementar `Dataset`, `Object`, `ObjectLink`.

```python
# instances/dataset.py
class Dataset(ResourceTypeBaseModel, table=True):
    """
    Contexto/escopo para Objects e ObjectLinks.
    Ex: "Vendas_Europa_2024", "Clientes_Brasil_2023"
    """
    __resource_type__ = "dataset"
    
    # Metadados do dataset
    version: str
    branch: Optional[str] = None

# instances/object.py
class Object(ResourceTypeBaseModel, table=True):
    """
    Instância de um ObjectType em um Dataset específico.
    Object = ObjectType + Dataset + valores das properties
    """
    __resource_type__ = "object"
    
    object_type_rid: str = Field(foreign_key="objecttype.rid")
    dataset_rid: str = Field(foreign_key="dataset.rid")
    
    # Valores das propriedades (JSON flexível)
    property_values: Dict[str, Any] = Field(sa_column=Column(JSON))

# instances/object_link.py
class ObjectLink(ResourceTypeBaseModel, table=True):
    """
    Instância de um LinkType conectando dois Objects em um Dataset.
    ObjectLink = LinkType + Dataset + Objects origem e destino
    """
    __resource_type__ = "object-link"
    
    link_type_rid: str = Field(foreign_key="linktype.rid", index=True)
    dataset_rid: str = Field(foreign_key="dataset.rid")
    
    # Conexão via PrimaryKeys dos objetos
    from_object_primary_key: str = Field(index=True)
    to_object_primary_key: str = Field(index=True)
```

---

### Prioridade BAIXA: Adicionar `references_object_type_api_name`

**Objetivo**: Tornar FKs explícitas e robustas.

**Ação**: Adicionar campo opcional no `PropertyType`:

```python
class PropertyType(ResourceTypeBaseModel, table=True):
    # ... campos existentes ...
    
    references_object_type_api_name: Optional[str] = Field(
        default=None,
        description="Se FK, indica o ObjectType referenciado"
    )
```

---

## 5. 📊 Roadmap de Implementação

### Fase 1: Correção do Metamodelo (1-2 dias)
1. ✅ **CONCLUÍDO**: Pydantic v2, multi-tenant, validações
2. 🔄 **PRÓXIMO**: Refatorar `LinkTypeSide` → `LinkType`
3. 🔄 **PRÓXIMO**: Adicionar `references_object_type_api_name`

### Fase 2: Camada de Dados (3-5 dias)
1. ⏳ Implementar `Dataset`
2. ⏳ Implementar `Object`
3. ⏳ Implementar `ObjectLink`
4. ⏳ Criar testes de integração end-to-end

### Fase 3: Validações e Performance (2-3 dias)
1. ⏳ Índices nas PKs de `ObjectLink`
2. ⏳ Validações de integridade referencial
3. ⏳ Testes de performance com grafos grandes

---

## 6. 🎯 Conclusão

### Status Atual vs Briefing

| Aspecto | Status | Nota |
|---------|--------|------|
| **Fundação (Registro)** | ✅ Excelente | 10/10 |
| **Camada Núcleo** | ✅ Completo | 10/10 |
| **Camada Metamodelo** | ⚠️ Quase Completo | 8/10 |
| **Camada de Dados** | ❌ Não Iniciado | 0/10 |
| **Alinhamento Foundry** | ⚠️ Parcial | 6/10 |

### Próximos Passos Críticos

1. **Refatorar LinkType** (2-3 horas)
   - Substituir `LinkTypeSide` por `LinkType` unificado
   - Alinhar com padrão Foundry e briefing
   
2. **Adicionar `references_object_type_api_name`** (1 hora)
   - Tornar FKs explícitas
   - Remover adivinhação por convenção de nomes
   
3. **Implementar Camada de Dados** (3-5 dias)
   - `Dataset`, `Object`, `ObjectLink`
   - Completar arquitetura do briefing

---

## 7. 📚 Referências

1. **Palantir Foundry SDK**: `foundry-platform-python` (GitHub)
2. **Foundry Documentation**: Ontology API v2
3. **Briefing do Projeto**: Modelo Conceitual em 3 Camadas
4. **Implementação Atual**: Projeto `registro` + `ontologia`

---

**Resumo Final**: O projeto está **muito bem implementado** nas camadas base (Núcleo e parte do Metamodelo). As principais melhorias são:
1. Refatorar `LinkType` para bidirecionali dade explícita (alinha com Foundry + Briefing)
2. Tornar FKs explícitas (robustez)
3. Implementar Camada de Dados (completar arquitetura)

O código já está em **qualidade profissional** e essas melhorias o tornarão **enterprise-grade completo**. 🚀
