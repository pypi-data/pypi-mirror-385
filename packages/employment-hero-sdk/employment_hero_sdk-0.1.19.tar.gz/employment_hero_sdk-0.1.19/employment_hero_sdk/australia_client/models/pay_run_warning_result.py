from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.pay_run_warning_dto import PayRunWarningDto


T = TypeVar("T", bound="PayRunWarningResult")


@_attrs_define
class PayRunWarningResult:
    """
    Attributes:
        warning_message (Union[Unset, str]):
        warnings (Union[Unset, List['PayRunWarningDto']]):
        template_name (Union[Unset, str]):
    """

    warning_message: Union[Unset, str] = UNSET
    warnings: Union[Unset, List["PayRunWarningDto"]] = UNSET
    template_name: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        warning_message = self.warning_message

        warnings: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.warnings, Unset):
            warnings = []
            for warnings_item_data in self.warnings:
                warnings_item = warnings_item_data.to_dict()
                warnings.append(warnings_item)

        template_name = self.template_name

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if warning_message is not UNSET:
            field_dict["warningMessage"] = warning_message
        if warnings is not UNSET:
            field_dict["warnings"] = warnings
        if template_name is not UNSET:
            field_dict["templateName"] = template_name

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.pay_run_warning_dto import PayRunWarningDto

        d = src_dict.copy()
        warning_message = d.pop("warningMessage", UNSET)

        warnings = []
        _warnings = d.pop("warnings", UNSET)
        for warnings_item_data in _warnings or []:
            warnings_item = PayRunWarningDto.from_dict(warnings_item_data)

            warnings.append(warnings_item)

        template_name = d.pop("templateName", UNSET)

        pay_run_warning_result = cls(
            warning_message=warning_message,
            warnings=warnings,
            template_name=template_name,
        )

        pay_run_warning_result.additional_properties = d
        return pay_run_warning_result

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
