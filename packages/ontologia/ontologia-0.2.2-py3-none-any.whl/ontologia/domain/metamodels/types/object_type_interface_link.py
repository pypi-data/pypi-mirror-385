"""
object_type_interface_link.py
-----------------------------
Association (link) model between ObjectType and InterfaceType for many-to-many.

Kept in a separate module to avoid circular imports when used in Relationship()
from both sides.
"""

from sqlmodel import Field, SQLModel


class ObjectTypeInterfaceLink(SQLModel, table=True):
    __tablename__ = "objecttype_interfacetype"

    object_type_rid: str = Field(foreign_key="objecttype.rid", primary_key=True, index=True)
    interface_type_rid: str = Field(foreign_key="interfacetype.rid", primary_key=True, index=True)
