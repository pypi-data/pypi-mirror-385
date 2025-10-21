from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.business_metadata_omop_model import BusinessMetadataOmopModel
    from ..models.employee_metadata_omop_model import EmployeeMetadataOmopModel


T = TypeVar("T", bound="UserAccountMetadataOmopModel")


@_attrs_define
class UserAccountMetadataOmopModel:
    """
    Attributes:
        id (Union[Unset, int]):
        email (Union[Unset, str]):
        businesses (Union[Unset, List['BusinessMetadataOmopModel']]):
        employees (Union[Unset, List['EmployeeMetadataOmopModel']]):
    """

    id: Union[Unset, int] = UNSET
    email: Union[Unset, str] = UNSET
    businesses: Union[Unset, List["BusinessMetadataOmopModel"]] = UNSET
    employees: Union[Unset, List["EmployeeMetadataOmopModel"]] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        id = self.id

        email = self.email

        businesses: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.businesses, Unset):
            businesses = []
            for businesses_item_data in self.businesses:
                businesses_item = businesses_item_data.to_dict()
                businesses.append(businesses_item)

        employees: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.employees, Unset):
            employees = []
            for employees_item_data in self.employees:
                employees_item = employees_item_data.to_dict()
                employees.append(employees_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if email is not UNSET:
            field_dict["email"] = email
        if businesses is not UNSET:
            field_dict["businesses"] = businesses
        if employees is not UNSET:
            field_dict["employees"] = employees

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.business_metadata_omop_model import BusinessMetadataOmopModel
        from ..models.employee_metadata_omop_model import EmployeeMetadataOmopModel

        d = src_dict.copy()
        id = d.pop("id", UNSET)

        email = d.pop("email", UNSET)

        businesses = []
        _businesses = d.pop("businesses", UNSET)
        for businesses_item_data in _businesses or []:
            businesses_item = BusinessMetadataOmopModel.from_dict(businesses_item_data)

            businesses.append(businesses_item)

        employees = []
        _employees = d.pop("employees", UNSET)
        for employees_item_data in _employees or []:
            employees_item = EmployeeMetadataOmopModel.from_dict(employees_item_data)

            employees.append(employees_item)

        user_account_metadata_omop_model = cls(
            id=id,
            email=email,
            businesses=businesses,
            employees=employees,
        )

        user_account_metadata_omop_model.additional_properties = d
        return user_account_metadata_omop_model

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
