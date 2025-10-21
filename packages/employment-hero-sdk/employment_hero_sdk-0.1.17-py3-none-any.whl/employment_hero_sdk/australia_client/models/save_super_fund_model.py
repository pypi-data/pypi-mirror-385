from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="SaveSuperFundModel")


@_attrs_define
class SaveSuperFundModel:
    """
    Attributes:
        member_number (Union[Unset, str]):
        allocated_percentage (Union[Unset, float]):
        fixed_amount (Union[Unset, float]):
        product_code (Union[Unset, str]): Nullable</p><p>Must be "SMSF" for a self managed super fund
        fund_name (Union[Unset, str]):
        allocate_balance (Union[Unset, bool]):
        is_employer_nominated_fund (Union[Unset, bool]):
    """

    member_number: Union[Unset, str] = UNSET
    allocated_percentage: Union[Unset, float] = UNSET
    fixed_amount: Union[Unset, float] = UNSET
    product_code: Union[Unset, str] = UNSET
    fund_name: Union[Unset, str] = UNSET
    allocate_balance: Union[Unset, bool] = UNSET
    is_employer_nominated_fund: Union[Unset, bool] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        member_number = self.member_number

        allocated_percentage = self.allocated_percentage

        fixed_amount = self.fixed_amount

        product_code = self.product_code

        fund_name = self.fund_name

        allocate_balance = self.allocate_balance

        is_employer_nominated_fund = self.is_employer_nominated_fund

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if member_number is not UNSET:
            field_dict["memberNumber"] = member_number
        if allocated_percentage is not UNSET:
            field_dict["allocatedPercentage"] = allocated_percentage
        if fixed_amount is not UNSET:
            field_dict["fixedAmount"] = fixed_amount
        if product_code is not UNSET:
            field_dict["productCode"] = product_code
        if fund_name is not UNSET:
            field_dict["fundName"] = fund_name
        if allocate_balance is not UNSET:
            field_dict["allocateBalance"] = allocate_balance
        if is_employer_nominated_fund is not UNSET:
            field_dict["isEmployerNominatedFund"] = is_employer_nominated_fund

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        member_number = d.pop("memberNumber", UNSET)

        allocated_percentage = d.pop("allocatedPercentage", UNSET)

        fixed_amount = d.pop("fixedAmount", UNSET)

        product_code = d.pop("productCode", UNSET)

        fund_name = d.pop("fundName", UNSET)

        allocate_balance = d.pop("allocateBalance", UNSET)

        is_employer_nominated_fund = d.pop("isEmployerNominatedFund", UNSET)

        save_super_fund_model = cls(
            member_number=member_number,
            allocated_percentage=allocated_percentage,
            fixed_amount=fixed_amount,
            product_code=product_code,
            fund_name=fund_name,
            allocate_balance=allocate_balance,
            is_employer_nominated_fund=is_employer_nominated_fund,
        )

        save_super_fund_model.additional_properties = d
        return save_super_fund_model

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
