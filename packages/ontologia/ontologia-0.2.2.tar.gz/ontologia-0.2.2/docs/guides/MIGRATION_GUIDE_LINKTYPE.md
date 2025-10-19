# Guia de Migração: LinkTypeSide → LinkType Unificado

**Data**: 2025-10-01  
**Objetivo**: Migrar de `LinkTypeSide` para `LinkType` unificado (padrão Foundry)

---

## 📋 **Comparação: Antes vs Depois**

### **ANTES: LinkTypeSide (Implementação Atual)**

```python
# ❌ Problema: Precisa criar 2 registros para uma relação completa

# Registro 1: Employee → Company
link_forward = LinkTypeSide(
    service="ontology",
    instance="main",
    api_name="works_for",
    display_name="Works For",
    cardinality=Cardinality.MANY,  # ⚠️ Cardinalidade apenas de UM lado
    object_type_api_name="employee",
    target_object_type_api_name="company"
)

# Registro 2: Company → Employee (separado!)
link_inverse = LinkTypeSide(
    service="ontology",
    instance="main",
    api_name="has_employees",  # ⚠️ Nome do inverso em registro separado
    display_name="Has Employees",
    cardinality=Cardinality.ONE,  # ⚠️ Outro lado da cardinalidade
    object_type_api_name="company",
    target_object_type_api_name="employee"
)

# ❌ Problemas:
# 1. Dois registros no banco para uma relação
# 2. Não há garantia de consistência entre os dois lados
# 3. Pode criar lado forward sem inverse
# 4. Cardinalidade fragmentada (MANY + ONE em vez de MANY_TO_ONE)
```

---

### **DEPOIS: LinkType Unificado (Nova Implementação)**

```python
# ✅ Solução: Um único registro define a relação completa

link = LinkType(
    service="ontology",
    instance="main",
    
    # Forward direction
    api_name="works_for",
    display_name="Works For",
    from_object_type_api_name="employee",
    to_object_type_api_name="company",
    
    # Inverse direction (definido atomicamente)
    inverse_api_name="has_employees",
    inverse_display_name="Has Employees",
    
    # Cardinalidade da relação completa
    cardinality=Cardinality.MANY_TO_ONE,  # ✅ Semântica completa
    
    # Constraints opcionais
    max_degree_forward=1,  # Employee trabalha em 1 company
    max_degree_inverse=None  # Company tem N employees
)

link.validate_and_resolve_object_types(session)
session.add(link)
session.commit()

# ✅ Vantagens:
# 1. Um único registro no banco
# 2. Consistência garantida (forward + inverse criados juntos)
# 3. Impossível criar relação incompleta
# 4. Cardinalidade semântica clara (MANY_TO_ONE)
```

---

## 📊 **Tabela Comparativa**

| Aspecto | LinkTypeSide (Atual) | LinkType (Novo) | Vencedor |
|---------|---------------------|-----------------|----------|
| **Registros no DB** | 2 | 1 | ✅ Novo |
| **Consistência** | Manual (dois registros) | Atômica | ✅ Novo |
| **Cardinalidade** | Fragmentada (MANY/ONE) | Completa (MANY_TO_ONE) | ✅ Novo |
| **Inverso** | Implícito | Explícito | ✅ Novo |
| **Padrão Foundry** | ❌ Não | ✅ Sim | ✅ Novo |
| **Briefing do Projeto** | ⚠️ Parcial | ✅ Completo | ✅ Novo |

---

## 🔄 **Como Migrar Código Existente**

### Passo 1: Identificar Links Existentes

```python
# ANTES: Buscar os dois lados separadamente
from ontologia.domain.metamodels.types.link_type import LinkTypeSide

forward_side = session.exec(
    select(LinkTypeSide).where(LinkTypeSide.api_name == "works_for")
).first()

inverse_side = session.exec(
    select(LinkTypeSide).where(LinkTypeSide.api_name == "has_employees")
).first()
```

### Passo 2: Criar LinkType Unificado

```python
# DEPOIS: Criar um único LinkType
from ontologia.domain.metamodels.types.link_type_unified import LinkType, Cardinality

unified_link = LinkType(
    service=forward_side.service,
    instance=forward_side.instance,
    
    # Dados do lado forward
    api_name=forward_side.api_name,
    display_name=forward_side.display_name,
    from_object_type_api_name=forward_side.object_type_api_name,
    to_object_type_api_name=forward_side.target_object_type_api_name,
    
    # Dados do lado inverse
    inverse_api_name=inverse_side.api_name,
    inverse_display_name=inverse_side.display_name,
    
    # Cardinalidade combinada
    cardinality=_combine_cardinality(forward_side.cardinality, inverse_side.cardinality),
    
    # Max degrees
    max_degree_forward=forward_side.max_degree,
    max_degree_inverse=inverse_side.max_degree
)

def _combine_cardinality(forward: Cardinality, inverse: Cardinality) -> Cardinality:
    """Combina cardinalidades dos dois lados em uma única."""
    if forward == "MANY" and inverse == "ONE":
        return Cardinality.MANY_TO_ONE
    elif forward == "ONE" and inverse == "MANY":
        return Cardinality.ONE_TO_MANY
    elif forward == "ONE" and inverse == "ONE":
        return Cardinality.ONE_TO_ONE
    elif forward == "MANY" and inverse == "MANY":
        return Cardinality.MANY_TO_MANY
    else:
        raise ValueError(f"Invalid cardinality combination: {forward}, {inverse}")
```

### Passo 3: Validar e Salvar

```python
unified_link.validate_and_resolve_object_types(session)
session.add(unified_link)
session.commit()
```

### Passo 4: Remover LinkTypeSides Antigos

```python
# Após confirmar que unified_link funciona:
session.delete(forward_side)
session.delete(inverse_side)
session.commit()
```

---

## 📝 **Script de Migração Completo**

```python
"""
migrate_to_unified_linktype.py
------------------------------
Script para migrar LinkTypeSides existentes para LinkType unificado.
"""

from sqlmodel import Session, select, create_engine
from ontologia.domain.metamodels.types.link_type import LinkTypeSide
from ontologia.domain.metamodels.types.link_type_unified import LinkType, Cardinality

def migrate_linktype_pairs(session: Session):
    """
    Migra pares de LinkTypeSides para LinkTypes unificados.
    
    Assume que:
    - Os LinkTypeSides estão em pares (forward + inverse)
    - Os pares podem ser identificados por object_types complementares
    """
    
    all_sides = session.exec(select(LinkTypeSide)).all()
    processed_rids = set()
    migrated_count = 0
    
    for forward_side in all_sides:
        if forward_side.rid in processed_rids:
            continue
        
        # Buscar o lado inverso correspondente
        inverse_side = session.exec(
            select(LinkTypeSide).where(
                (LinkTypeSide.object_type_api_name == forward_side.target_object_type_api_name) &
                (LinkTypeSide.target_object_type_api_name == forward_side.object_type_api_name) &
                (LinkTypeSide.service == forward_side.service) &
                (LinkTypeSide.instance == forward_side.instance)
            )
        ).first()
        
        if not inverse_side:
            print(f"⚠️  Warning: No inverse found for {forward_side.api_name}, skipping...")
            continue
        
        # Criar LinkType unificado
        try:
            unified_link = LinkType(
                service=forward_side.service,
                instance=forward_side.instance,
                
                api_name=forward_side.api_name,
                display_name=forward_side.display_name,
                description=forward_side.description or "",
                
                from_object_type_api_name=forward_side.object_type_api_name,
                to_object_type_api_name=forward_side.target_object_type_api_name,
                
                inverse_api_name=inverse_side.api_name,
                inverse_display_name=inverse_side.display_name,
                
                cardinality=_infer_cardinality(forward_side, inverse_side),
                
                max_degree_forward=forward_side.max_degree,
                max_degree_inverse=inverse_side.max_degree
            )
            
            unified_link.validate_and_resolve_object_types(session)
            session.add(unified_link)
            
            # Marcar como processados
            processed_rids.add(forward_side.rid)
            processed_rids.add(inverse_side.rid)
            
            print(f"✅ Migrated: {forward_side.api_name} ↔ {inverse_side.api_name}")
            migrated_count += 1
            
        except Exception as e:
            print(f"❌ Error migrating {forward_side.api_name}: {e}")
            session.rollback()
            continue
    
    # Commit todas as migrações
    session.commit()
    
    print(f"\n🎉 Migration complete: {migrated_count} LinkType(s) created")
    
    # Opcional: Remover LinkTypeSides antigos
    # for rid in processed_rids:
    #     old_side = session.get(LinkTypeSide, rid)
    #     if old_side:
    #         session.delete(old_side)
    # session.commit()

def _infer_cardinality(forward: LinkTypeSide, inverse: LinkTypeSide) -> Cardinality:
    """Infere a cardinalidade completa a partir dos dois lados."""
    from ontologia.domain.metamodels.types.link_type import Cardinality as OldCardinality
    
    # Map old enum to new
    forward_card = "MANY" if forward.cardinality == OldCardinality.MANY else "ONE"
    inverse_card = "MANY" if inverse.cardinality == OldCardinality.MANY else "ONE"
    
    if forward_card == "MANY" and inverse_card == "ONE":
        return Cardinality.MANY_TO_ONE
    elif forward_card == "ONE" and inverse_card == "MANY":
        return Cardinality.ONE_TO_MANY
    elif forward_card == "ONE" and inverse_card == "ONE":
        return Cardinality.ONE_TO_ONE
    elif forward_card == "MANY" and inverse_card == "MANY":
        return Cardinality.MANY_TO_MANY
    else:
        raise ValueError(f"Invalid cardinality: {forward_card}, {inverse_card}")

if __name__ == "__main__":
    engine = create_engine("sqlite:///./ontology.db")
    with Session(engine) as session:
        migrate_linktype_pairs(session)
```

---

## ⚠️ **Breaking Changes**

### 1. Mudança de Nome do Modelo

```python
# ANTES
from ontologia.domain.metamodels.types.link_type import LinkTypeSide

# DEPOIS
from ontologia.domain.metamodels.types.link_type_unified import LinkType
```

### 2. Enum de Cardinalidade

```python
# ANTES
class Cardinality(str, enum.Enum):
    ONE = "ONE"
    MANY = "MANY"

# DEPOIS
class Cardinality(str, enum.Enum):
    ONE_TO_ONE = "ONE_TO_ONE"
    ONE_TO_MANY = "ONE_TO_MANY"
    MANY_TO_ONE = "MANY_TO_ONE"
    MANY_TO_MANY = "MANY_TO_MANY"
```

### 3. Campos Obrigatórios

```python
# ANTES: target_object_type_api_name era opcional
LinkTypeSide(
    object_type_api_name="employee",
    # target pode ser None se usar FK
)

# DEPOIS: Ambos os lados são obrigatórios
LinkType(
    from_object_type_api_name="employee",
    to_object_type_api_name="company",  # Obrigatório!
    inverse_api_name="has_employees",    # Obrigatório!
    inverse_display_name="Has Employees" # Obrigatório!
)
```

---

## ✅ **Checklist de Migração**

- [ ] **Backup do banco de dados**
- [ ] Analisar todos os `LinkTypeSides` existentes
- [ ] Identificar pares forward/inverse
- [ ] Executar script de migração
- [ ] Validar que `LinkTypes` foram criados corretamente
- [ ] Atualizar código da aplicação para usar `LinkType`
- [ ] Atualizar testes
- [ ] (Opcional) Remover `LinkTypeSides` antigos
- [ ] Atualizar documentação

---

## 📚 **Recursos Adicionais**

1. **`FOUNDRY_ANALYSIS_AND_RECOMMENDATIONS.md`** - Análise completa do Foundry
2. **`link_type_unified.py`** - Código fonte do novo modelo
3. **`example_unified_linktype.py`** - Exemplos de uso
4. **Foundry SDK**: https://github.com/palantir/foundry-platform-python

---

## 🎯 **Próximos Passos Após Migração**

1. **Implementar Camada de Dados**
   - `Dataset` (contexto para Objects/Links)
   - `Object` (instâncias de ObjectType)
   - `ObjectLink` (instâncias de LinkType)

2. **Adicionar `references_object_type_api_name`**
   - Tornar FKs explícitas em `PropertyType`
   - Remover adivinhação por convenção de nomes

3. **Testes End-to-End**
   - Criar ObjectTypes
   - Criar LinkTypes
   - Criar Objects
   - Criar ObjectLinks
   - Navegar grafo

---

**Resultado Final**: Ontologia 100% alinhada com Palantir Foundry e com o briefing do projeto! 🚀
