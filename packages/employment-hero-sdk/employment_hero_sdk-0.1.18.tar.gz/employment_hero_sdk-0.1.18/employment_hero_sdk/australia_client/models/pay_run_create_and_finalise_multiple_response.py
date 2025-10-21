from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.pay_run_create_and_finalise_multiple_result import PayRunCreateAndFinaliseMultipleResult


T = TypeVar("T", bound="PayRunCreateAndFinaliseMultipleResponse")


@_attrs_define
class PayRunCreateAndFinaliseMultipleResponse:
    """
    Attributes:
        results (Union[Unset, List['PayRunCreateAndFinaliseMultipleResult']]):
    """

    results: Union[Unset, List["PayRunCreateAndFinaliseMultipleResult"]] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        results: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.results, Unset):
            results = []
            for results_item_data in self.results:
                results_item = results_item_data.to_dict()
                results.append(results_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if results is not UNSET:
            field_dict["results"] = results

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.pay_run_create_and_finalise_multiple_result import PayRunCreateAndFinaliseMultipleResult

        d = src_dict.copy()
        results = []
        _results = d.pop("results", UNSET)
        for results_item_data in _results or []:
            results_item = PayRunCreateAndFinaliseMultipleResult.from_dict(results_item_data)

            results.append(results_item)

        pay_run_create_and_finalise_multiple_response = cls(
            results=results,
        )

        pay_run_create_and_finalise_multiple_response.additional_properties = d
        return pay_run_create_and_finalise_multiple_response

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
