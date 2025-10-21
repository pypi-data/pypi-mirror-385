from enum import Enum


class SingleValueNodeQueryNodeKind(str, Enum):
    ALL = "All"
    ANY = "Any"
    BINARYOPERATOR = "BinaryOperator"
    COLLECTIONFUNCTIONCALL = "CollectionFunctionCall"
    COLLECTIONNAVIGATIONNODE = "CollectionNavigationNode"
    COLLECTIONPROPERTYACCESS = "CollectionPropertyAccess"
    CONSTANT = "Constant"
    CONVERT = "Convert"
    ENTITYCOLLECTIONCAST = "EntityCollectionCast"
    ENTITYCOLLECTIONFUNCTIONCALL = "EntityCollectionFunctionCall"
    ENTITYRANGEVARIABLEREFERENCE = "EntityRangeVariableReference"
    NAMEDFUNCTIONPARAMETER = "NamedFunctionParameter"
    NONE = "None"
    NONENTITYRANGEVARIABLEREFERENCE = "NonentityRangeVariableReference"
    SINGLEENTITYCAST = "SingleEntityCast"
    SINGLEENTITYFUNCTIONCALL = "SingleEntityFunctionCall"
    SINGLENAVIGATIONNODE = "SingleNavigationNode"
    SINGLEVALUEFUNCTIONCALL = "SingleValueFunctionCall"
    SINGLEVALUEOPENPROPERTYACCESS = "SingleValueOpenPropertyAccess"
    SINGLEVALUEPROPERTYACCESS = "SingleValuePropertyAccess"
    UNARYOPERATOR = "UnaryOperator"

    def __str__(self) -> str:
        return str(self.value)
