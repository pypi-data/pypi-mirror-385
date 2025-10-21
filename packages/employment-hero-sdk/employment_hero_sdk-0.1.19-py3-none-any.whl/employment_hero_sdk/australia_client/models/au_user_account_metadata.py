from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.au_available_business_model import AuAvailableBusinessModel
    from ..models.available_employee_model import AvailableEmployeeModel


T = TypeVar("T", bound="AuUserAccountMetadata")


@_attrs_define
class AuUserAccountMetadata:
    """
    Attributes:
        id (Union[Unset, int]):
        email (Union[Unset, str]):
        employees (Union[Unset, List['AvailableEmployeeModel']]):
        businesses (Union[Unset, List['AuAvailableBusinessModel']]):
    """

    id: Union[Unset, int] = UNSET
    email: Union[Unset, str] = UNSET
    employees: Union[Unset, List["AvailableEmployeeModel"]] = UNSET
    businesses: Union[Unset, List["AuAvailableBusinessModel"]] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        id = self.id

        email = self.email

        employees: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.employees, Unset):
            employees = []
            for employees_item_data in self.employees:
                employees_item = employees_item_data.to_dict()
                employees.append(employees_item)

        businesses: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.businesses, Unset):
            businesses = []
            for businesses_item_data in self.businesses:
                businesses_item = businesses_item_data.to_dict()
                businesses.append(businesses_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if email is not UNSET:
            field_dict["email"] = email
        if employees is not UNSET:
            field_dict["employees"] = employees
        if businesses is not UNSET:
            field_dict["businesses"] = businesses

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.au_available_business_model import AuAvailableBusinessModel
        from ..models.available_employee_model import AvailableEmployeeModel

        d = src_dict.copy()
        id = d.pop("id", UNSET)

        email = d.pop("email", UNSET)

        employees = []
        _employees = d.pop("employees", UNSET)
        for employees_item_data in _employees or []:
            employees_item = AvailableEmployeeModel.from_dict(employees_item_data)

            employees.append(employees_item)

        businesses = []
        _businesses = d.pop("businesses", UNSET)
        for businesses_item_data in _businesses or []:
            businesses_item = AuAvailableBusinessModel.from_dict(businesses_item_data)

            businesses.append(businesses_item)

        au_user_account_metadata = cls(
            id=id,
            email=email,
            employees=employees,
            businesses=businesses,
        )

        au_user_account_metadata.additional_properties = d
        return au_user_account_metadata

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
