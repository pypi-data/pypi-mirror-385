from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.pay_run_finalise_result import PayRunFinaliseResult


T = TypeVar("T", bound="PayRunCreateAndFinaliseMultipleResult")


@_attrs_define
class PayRunCreateAndFinaliseMultipleResult:
    """
    Attributes:
        pay_run_id (Union[Unset, int]):
        finalise_result (Union[Unset, PayRunFinaliseResult]):
    """

    pay_run_id: Union[Unset, int] = UNSET
    finalise_result: Union[Unset, "PayRunFinaliseResult"] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        pay_run_id = self.pay_run_id

        finalise_result: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.finalise_result, Unset):
            finalise_result = self.finalise_result.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if pay_run_id is not UNSET:
            field_dict["payRunId"] = pay_run_id
        if finalise_result is not UNSET:
            field_dict["finaliseResult"] = finalise_result

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.pay_run_finalise_result import PayRunFinaliseResult

        d = src_dict.copy()
        pay_run_id = d.pop("payRunId", UNSET)

        _finalise_result = d.pop("finaliseResult", UNSET)
        finalise_result: Union[Unset, PayRunFinaliseResult]
        if isinstance(_finalise_result, Unset):
            finalise_result = UNSET
        else:
            finalise_result = PayRunFinaliseResult.from_dict(_finalise_result)

        pay_run_create_and_finalise_multiple_result = cls(
            pay_run_id=pay_run_id,
            finalise_result=finalise_result,
        )

        pay_run_create_and_finalise_multiple_result.additional_properties = d
        return pay_run_create_and_finalise_multiple_result

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
