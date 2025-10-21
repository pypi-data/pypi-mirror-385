from enum import Enum


class IEdmTypeEdmTypeKind(str, Enum):
    COLLECTION = "Collection"
    COMPLEX = "Complex"
    ENTITY = "Entity"
    ENTITYREFERENCE = "EntityReference"
    ENUM = "Enum"
    NONE = "None"
    PRIMITIVE = "Primitive"
    ROW = "Row"

    def __str__(self) -> str:
        return str(self.value)
