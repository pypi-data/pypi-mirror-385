"""
Ontologia - An ontology management system built on Registro and SQLModel.

This package provides tools for defining and managing ontologies with:
- Object types with properties and relationships
- Rich data type system
- Validation and persistence
- Data source integration
"""

__version__ = "0.1.1"

# Metamodel exports
from ontologia.domain.metamodels.instances.object_type_data_source import ObjectTypeDataSource
from ontologia.domain.metamodels.types.link_type import Cardinality, LinkType
from ontologia.domain.metamodels.types.object_type import ObjectType
from ontologia.domain.metamodels.types.property_type import PropertyType

__all__ = [
    "ObjectType",
    "PropertyType",
    "LinkType",
    "Cardinality",
    "ObjectTypeDataSource",
]
