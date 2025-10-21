from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.au_ess_bank_account_model import AuEssBankAccountModel


T = TypeVar("T", bound="AuEssSaveBankAccountResponseModel")


@_attrs_define
class AuEssSaveBankAccountResponseModel:
    """
    Attributes:
        validation_warning (Union[Unset, str]):
        result (Union[Unset, AuEssBankAccountModel]):
    """

    validation_warning: Union[Unset, str] = UNSET
    result: Union[Unset, "AuEssBankAccountModel"] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        validation_warning = self.validation_warning

        result: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.result, Unset):
            result = self.result.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if validation_warning is not UNSET:
            field_dict["validationWarning"] = validation_warning
        if result is not UNSET:
            field_dict["result"] = result

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.au_ess_bank_account_model import AuEssBankAccountModel

        d = src_dict.copy()
        validation_warning = d.pop("validationWarning", UNSET)

        _result = d.pop("result", UNSET)
        result: Union[Unset, AuEssBankAccountModel]
        if isinstance(_result, Unset):
            result = UNSET
        else:
            result = AuEssBankAccountModel.from_dict(_result)

        au_ess_save_bank_account_response_model = cls(
            validation_warning=validation_warning,
            result=result,
        )

        au_ess_save_bank_account_response_model.additional_properties = d
        return au_ess_save_bank_account_response_model

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
