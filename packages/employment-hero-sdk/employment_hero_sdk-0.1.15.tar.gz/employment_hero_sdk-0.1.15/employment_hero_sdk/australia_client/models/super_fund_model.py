from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.super_product_model import SuperProductModel


T = TypeVar("T", bound="SuperFundModel")


@_attrs_define
class SuperFundModel:
    """
    Attributes:
        id (Union[Unset, int]):
        employee_id (Union[Unset, int]):
        name (Union[Unset, str]):
        member_number (Union[Unset, str]):
        allocated_percentage (Union[Unset, float]):
        fixed_amount (Union[Unset, float]):
        super_product (Union[Unset, SuperProductModel]):
        allocate_balance (Union[Unset, bool]):
        can_be_deleted (Union[Unset, bool]):
        is_employer_nominated_fund (Union[Unset, bool]):
    """

    id: Union[Unset, int] = UNSET
    employee_id: Union[Unset, int] = UNSET
    name: Union[Unset, str] = UNSET
    member_number: Union[Unset, str] = UNSET
    allocated_percentage: Union[Unset, float] = UNSET
    fixed_amount: Union[Unset, float] = UNSET
    super_product: Union[Unset, "SuperProductModel"] = UNSET
    allocate_balance: Union[Unset, bool] = UNSET
    can_be_deleted: Union[Unset, bool] = UNSET
    is_employer_nominated_fund: Union[Unset, bool] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        id = self.id

        employee_id = self.employee_id

        name = self.name

        member_number = self.member_number

        allocated_percentage = self.allocated_percentage

        fixed_amount = self.fixed_amount

        super_product: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.super_product, Unset):
            super_product = self.super_product.to_dict()

        allocate_balance = self.allocate_balance

        can_be_deleted = self.can_be_deleted

        is_employer_nominated_fund = self.is_employer_nominated_fund

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if employee_id is not UNSET:
            field_dict["employeeId"] = employee_id
        if name is not UNSET:
            field_dict["name"] = name
        if member_number is not UNSET:
            field_dict["memberNumber"] = member_number
        if allocated_percentage is not UNSET:
            field_dict["allocatedPercentage"] = allocated_percentage
        if fixed_amount is not UNSET:
            field_dict["fixedAmount"] = fixed_amount
        if super_product is not UNSET:
            field_dict["superProduct"] = super_product
        if allocate_balance is not UNSET:
            field_dict["allocateBalance"] = allocate_balance
        if can_be_deleted is not UNSET:
            field_dict["canBeDeleted"] = can_be_deleted
        if is_employer_nominated_fund is not UNSET:
            field_dict["isEmployerNominatedFund"] = is_employer_nominated_fund

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.super_product_model import SuperProductModel

        d = src_dict.copy()
        id = d.pop("id", UNSET)

        employee_id = d.pop("employeeId", UNSET)

        name = d.pop("name", UNSET)

        member_number = d.pop("memberNumber", UNSET)

        allocated_percentage = d.pop("allocatedPercentage", UNSET)

        fixed_amount = d.pop("fixedAmount", UNSET)

        _super_product = d.pop("superProduct", UNSET)
        super_product: Union[Unset, SuperProductModel]
        if isinstance(_super_product, Unset):
            super_product = UNSET
        else:
            super_product = SuperProductModel.from_dict(_super_product)

        allocate_balance = d.pop("allocateBalance", UNSET)

        can_be_deleted = d.pop("canBeDeleted", UNSET)

        is_employer_nominated_fund = d.pop("isEmployerNominatedFund", UNSET)

        super_fund_model = cls(
            id=id,
            employee_id=employee_id,
            name=name,
            member_number=member_number,
            allocated_percentage=allocated_percentage,
            fixed_amount=fixed_amount,
            super_product=super_product,
            allocate_balance=allocate_balance,
            can_be_deleted=can_be_deleted,
            is_employer_nominated_fund=is_employer_nominated_fund,
        )

        super_fund_model.additional_properties = d
        return super_fund_model

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
