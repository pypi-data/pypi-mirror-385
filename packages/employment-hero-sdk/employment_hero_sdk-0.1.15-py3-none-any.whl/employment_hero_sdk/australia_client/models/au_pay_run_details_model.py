from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.au_pay_run_grand_total_model import AuPayRunGrandTotalModel
    from ..models.au_pay_run_total_detail_model import AuPayRunTotalDetailModel
    from ..models.pay_run_model import PayRunModel


T = TypeVar("T", bound="AuPayRunDetailsModel")


@_attrs_define
class AuPayRunDetailsModel:
    """
    Attributes:
        pay_run_totals (Union[Unset, List['AuPayRunTotalDetailModel']]):
        grand_total (Union[Unset, AuPayRunGrandTotalModel]):
        pay_run (Union[Unset, PayRunModel]):
    """

    pay_run_totals: Union[Unset, List["AuPayRunTotalDetailModel"]] = UNSET
    grand_total: Union[Unset, "AuPayRunGrandTotalModel"] = UNSET
    pay_run: Union[Unset, "PayRunModel"] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        pay_run_totals: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.pay_run_totals, Unset):
            pay_run_totals = []
            for pay_run_totals_item_data in self.pay_run_totals:
                pay_run_totals_item = pay_run_totals_item_data.to_dict()
                pay_run_totals.append(pay_run_totals_item)

        grand_total: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.grand_total, Unset):
            grand_total = self.grand_total.to_dict()

        pay_run: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.pay_run, Unset):
            pay_run = self.pay_run.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if pay_run_totals is not UNSET:
            field_dict["payRunTotals"] = pay_run_totals
        if grand_total is not UNSET:
            field_dict["grandTotal"] = grand_total
        if pay_run is not UNSET:
            field_dict["payRun"] = pay_run

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.au_pay_run_grand_total_model import AuPayRunGrandTotalModel
        from ..models.au_pay_run_total_detail_model import AuPayRunTotalDetailModel
        from ..models.pay_run_model import PayRunModel

        d = src_dict.copy()
        pay_run_totals = []
        _pay_run_totals = d.pop("payRunTotals", UNSET)
        for pay_run_totals_item_data in _pay_run_totals or []:
            pay_run_totals_item = AuPayRunTotalDetailModel.from_dict(pay_run_totals_item_data)

            pay_run_totals.append(pay_run_totals_item)

        _grand_total = d.pop("grandTotal", UNSET)
        grand_total: Union[Unset, AuPayRunGrandTotalModel]
        if isinstance(_grand_total, Unset):
            grand_total = UNSET
        else:
            grand_total = AuPayRunGrandTotalModel.from_dict(_grand_total)

        _pay_run = d.pop("payRun", UNSET)
        pay_run: Union[Unset, PayRunModel]
        if isinstance(_pay_run, Unset):
            pay_run = UNSET
        else:
            pay_run = PayRunModel.from_dict(_pay_run)

        au_pay_run_details_model = cls(
            pay_run_totals=pay_run_totals,
            grand_total=grand_total,
            pay_run=pay_run,
        )

        au_pay_run_details_model.additional_properties = d
        return au_pay_run_details_model

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
