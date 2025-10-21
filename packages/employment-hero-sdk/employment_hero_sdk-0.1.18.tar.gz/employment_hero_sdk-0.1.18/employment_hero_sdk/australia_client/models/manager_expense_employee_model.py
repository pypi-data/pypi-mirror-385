from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ManagerExpenseEmployeeModel")


@_attrs_define
class ManagerExpenseEmployeeModel:
    """
    Attributes:
        can_create (Union[Unset, bool]):
        can_approve (Union[Unset, bool]):
        id (Union[Unset, int]):
        name (Union[Unset, str]):
        first_name (Union[Unset, str]):
        surname (Union[Unset, str]):
    """

    can_create: Union[Unset, bool] = UNSET
    can_approve: Union[Unset, bool] = UNSET
    id: Union[Unset, int] = UNSET
    name: Union[Unset, str] = UNSET
    first_name: Union[Unset, str] = UNSET
    surname: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        can_create = self.can_create

        can_approve = self.can_approve

        id = self.id

        name = self.name

        first_name = self.first_name

        surname = self.surname

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if can_create is not UNSET:
            field_dict["canCreate"] = can_create
        if can_approve is not UNSET:
            field_dict["canApprove"] = can_approve
        if id is not UNSET:
            field_dict["id"] = id
        if name is not UNSET:
            field_dict["name"] = name
        if first_name is not UNSET:
            field_dict["firstName"] = first_name
        if surname is not UNSET:
            field_dict["surname"] = surname

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        can_create = d.pop("canCreate", UNSET)

        can_approve = d.pop("canApprove", UNSET)

        id = d.pop("id", UNSET)

        name = d.pop("name", UNSET)

        first_name = d.pop("firstName", UNSET)

        surname = d.pop("surname", UNSET)

        manager_expense_employee_model = cls(
            can_create=can_create,
            can_approve=can_approve,
            id=id,
            name=name,
            first_name=first_name,
            surname=surname,
        )

        manager_expense_employee_model.additional_properties = d
        return manager_expense_employee_model

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
