from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.i_edm_model import IEdmModel
    from ..models.i_edm_type import IEdmType


T = TypeVar("T", bound="ODataQueryContext")


@_attrs_define
class ODataQueryContext:
    """
    Attributes:
        model (Union[Unset, IEdmModel]):
        element_type (Union[Unset, IEdmType]):
        element_clr_type (Union[Unset, str]):
    """

    model: Union[Unset, "IEdmModel"] = UNSET
    element_type: Union[Unset, "IEdmType"] = UNSET
    element_clr_type: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        model: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.model, Unset):
            model = self.model.to_dict()

        element_type: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.element_type, Unset):
            element_type = self.element_type.to_dict()

        element_clr_type = self.element_clr_type

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if model is not UNSET:
            field_dict["model"] = model
        if element_type is not UNSET:
            field_dict["elementType"] = element_type
        if element_clr_type is not UNSET:
            field_dict["elementClrType"] = element_clr_type

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.i_edm_model import IEdmModel
        from ..models.i_edm_type import IEdmType

        d = src_dict.copy()
        _model = d.pop("model", UNSET)
        model: Union[Unset, IEdmModel]
        if isinstance(_model, Unset):
            model = UNSET
        else:
            model = IEdmModel.from_dict(_model)

        _element_type = d.pop("elementType", UNSET)
        element_type: Union[Unset, IEdmType]
        if isinstance(_element_type, Unset):
            element_type = UNSET
        else:
            element_type = IEdmType.from_dict(_element_type)

        element_clr_type = d.pop("elementClrType", UNSET)

        o_data_query_context = cls(
            model=model,
            element_type=element_type,
            element_clr_type=element_clr_type,
        )

        o_data_query_context.additional_properties = d
        return o_data_query_context

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
