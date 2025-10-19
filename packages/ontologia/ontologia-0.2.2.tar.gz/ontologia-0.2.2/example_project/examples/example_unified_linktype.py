"""
example_unified_linktype.py
---------------------------
Exemplo de uso do novo LinkType unificado.
Demonstra como criar relações bidirecionais de forma atômica.
"""

from sqlmodel import Session, SQLModel, create_engine

from ontologia.domain.metamodels.types.link_type_unified import Cardinality, LinkType
from ontologia.domain.metamodels.types.object_type import ObjectType

# Configurar banco de dados
DATABASE_URL = "sqlite:///./test_unified_linktype.db"
engine = create_engine(DATABASE_URL, echo=True)


def setup_database():
    """Cria as tabelas no banco de dados."""
    SQLModel.metadata.create_all(engine)


def create_object_types(session: Session) -> tuple[ObjectType, ObjectType]:
    """Cria dois ObjectTypes: Employee e Company."""

    # Criar ObjectType: Employee
    employee_type = ObjectType(
        service="ontology",
        instance="main",
        api_name="employee",
        display_name="Employee",
        description="Represents an employee",
        primary_key_field="employee_id",
    )

    # Propriedades do Employee
    employee_type.set_properties(
        [
            {
                "api_name": "employee_id",
                "display_name": "Employee ID",
                "data_type": "string",
                "is_primary_key": True,
                "required": True,
            },
            {
                "api_name": "first_name",
                "display_name": "First Name",
                "data_type": "string",
                "required": True,
            },
            {
                "api_name": "last_name",
                "display_name": "Last Name",
                "data_type": "string",
                "required": True,
            },
        ]
    )

    session.add(employee_type)

    # Criar ObjectType: Company
    company_type = ObjectType(
        service="ontology",
        instance="main",
        api_name="company",
        display_name="Company",
        description="Represents a company",
        primary_key_field="company_id",
    )

    # Propriedades do Company
    company_type.set_properties(
        [
            {
                "api_name": "company_id",
                "display_name": "Company ID",
                "data_type": "string",
                "is_primary_key": True,
                "required": True,
            },
            {
                "api_name": "company_name",
                "display_name": "Company Name",
                "data_type": "string",
                "required": True,
            },
            {
                "api_name": "industry",
                "display_name": "Industry",
                "data_type": "string",
                "required": False,
            },
        ]
    )

    session.add(company_type)
    session.commit()
    session.refresh(employee_type)
    session.refresh(company_type)

    print("\n✅ Created ObjectTypes:")
    print(f"  - {employee_type.api_name} (RID: {employee_type.rid})")
    print(f"  - {company_type.api_name} (RID: {company_type.rid})")

    return employee_type, company_type


def create_employment_link(
    session: Session, employee_type: ObjectType, company_type: ObjectType
) -> LinkType:
    """
    Cria um LinkType bidirecional: Employee "works_for" Company.

    Esta é a nova abordagem unificada, onde:
    - Forward: Employee → Company ("works_for")
    - Inverse: Company → Employee ("has_employees")
    - Cardinalidade: MANY_TO_ONE (muitos employees para uma company)
    """

    employment_link = LinkType(
        service="ontology",
        instance="main",
        # Identificação do link (lado forward)
        api_name="works_for",
        display_name="Works For",
        description="Connects an employee to their employer company",
        # Cardinalidade da relação completa
        cardinality=Cardinality.MANY_TO_ONE,
        # Lado Forward (Employee → Company)
        from_object_type_api_name="employee",
        to_object_type_api_name="company",
        # Lado Inverse (Company → Employee)
        inverse_api_name="has_employees",
        inverse_display_name="Has Employees",
        # Constraints opcionais
        max_degree_forward=1,  # Cada employee trabalha em apenas 1 company
        max_degree_inverse=None,  # Uma company pode ter N employees
    )

    # Validar e resolver ObjectTypes
    employment_link.validate_and_resolve_object_types(session)

    session.add(employment_link)
    session.commit()
    session.refresh(employment_link)

    print("\n✅ Created LinkType:")
    print(f"  - RID: {employment_link.rid}")
    print(f"  - Forward: {employment_link.get_forward_definition()}")
    print(f"  - Inverse: {employment_link.get_inverse_definition()}")

    return employment_link


def create_partnership_link(session: Session, company_type: ObjectType) -> LinkType:
    """
    Cria um LinkType MANY_TO_MANY entre Companies (parceria).

    Demonstra:
    - Relação do mesmo ObjectType consigo mesmo
    - Cardinalidade MANY_TO_MANY
    """

    partnership_link = LinkType(
        service="ontology",
        instance="main",
        # Identificação
        api_name="partners_with",
        display_name="Partners With",
        description="Business partnership between companies",
        # MANY_TO_MANY: muitas companies podem ter muitas partners
        cardinality=Cardinality.MANY_TO_MANY,
        # Ambos os lados são "company"
        from_object_type_api_name="company",
        to_object_type_api_name="company",
        # Inverso (semanticamente simétrico, mas precisa nome diferente)
        inverse_api_name="partnered_by",
        inverse_display_name="Partnered By",
    )

    partnership_link.validate_and_resolve_object_types(session)

    session.add(partnership_link)
    session.commit()
    session.refresh(partnership_link)

    print("\n✅ Created Self-Referencing LinkType:")
    print(f"  - RID: {partnership_link.rid}")
    print(
        f"  - {partnership_link.cardinality}: {partnership_link.from_object_type_api_name} ↔ {partnership_link.to_object_type_api_name}"
    )

    return partnership_link


def demonstrate_link_queries(session: Session, employment_link: LinkType):
    """Demonstra como consultar informações sobre o link."""

    print("\n📊 Link Information:")
    print(f"  - API Name (forward): {employment_link.api_name}")
    print(f"  - API Name (inverse): {employment_link.inverse_api_name}")
    print(f"  - Cardinality: {employment_link.cardinality}")
    print(f"  - From: {employment_link.from_object_type_api_name}")
    print(f"  - To: {employment_link.to_object_type_api_name}")

    # Acessar definições estruturadas
    forward_def = employment_link.get_forward_definition()
    inverse_def = employment_link.get_inverse_definition()

    print("\n🔍 Forward Direction:")
    print(f"  - {forward_def['from']} → {forward_def['to']}")
    print(f"  - Cardinality from Employee perspective: {forward_def['cardinality']}")
    print(f"  - Max degree: {forward_def['max_degree']}")

    print("\n🔍 Inverse Direction:")
    print(f"  - {inverse_def['from']} → {inverse_def['to']}")
    print(f"  - Cardinality from Company perspective: {inverse_def['cardinality']}")
    print(f"  - Max degree: {inverse_def['max_degree']}")


def main():
    """Executa os exemplos."""
    print("=" * 70)
    print("EXEMPLO: LinkType Unificado (Padrão Foundry)")
    print("=" * 70)

    # Setup
    setup_database()

    with Session(engine) as session:
        # 1. Criar ObjectTypes
        employee_type, company_type = create_object_types(session)

        # 2. Criar LinkType MANY_TO_ONE (Employment)
        employment_link = create_employment_link(session, employee_type, company_type)

        # 3. Criar LinkType MANY_TO_MANY (Partnership)
        partnership_link = create_partnership_link(session, company_type)

        # 4. Demonstrar consultas
        demonstrate_link_queries(session, employment_link)

    print("\n" + "=" * 70)
    print("✅ Exemplo concluído com sucesso!")
    print("=" * 70)
    print("\nVantagens do LinkType Unificado:")
    print("  1. ✅ Relação bidirecional em um único registro")
    print("  2. ✅ Cardinalidade da relação completa (não de 'lados')")
    print("  3. ✅ Inverso explícito e atômico")
    print("  4. ✅ Alinhado com Palantir Foundry")
    print("  5. ✅ Alinhado com briefing do projeto")
    print("\nComparação com LinkTypeSide:")
    print("  - LinkTypeSide: 2 registros para relação completa")
    print("  - LinkType: 1 registro para relação completa ✅")


if __name__ == "__main__":
    main()
