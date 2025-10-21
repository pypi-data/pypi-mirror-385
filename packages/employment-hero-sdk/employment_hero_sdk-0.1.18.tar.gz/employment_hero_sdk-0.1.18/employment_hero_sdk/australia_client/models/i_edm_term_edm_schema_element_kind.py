from enum import Enum


class IEdmTermEdmSchemaElementKind(str, Enum):
    ENTITYCONTAINER = "EntityContainer"
    FUNCTION = "Function"
    NONE = "None"
    TYPEDEFINITION = "TypeDefinition"
    VALUETERM = "ValueTerm"

    def __str__(self) -> str:
        return str(self.value)
