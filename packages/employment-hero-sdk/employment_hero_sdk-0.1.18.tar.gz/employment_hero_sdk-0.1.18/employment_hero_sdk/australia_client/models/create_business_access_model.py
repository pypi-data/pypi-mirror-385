from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.create_business_access_model_related_user_type import CreateBusinessAccessModelRelatedUserType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.employee_group_access_model import EmployeeGroupAccessModel
    from ..models.kiosk_access_model import KioskAccessModel
    from ..models.location_access_model import LocationAccessModel
    from ..models.payroll_access_model import PayrollAccessModel
    from ..models.report_access_model import ReportAccessModel


T = TypeVar("T", bound="CreateBusinessAccessModel")


@_attrs_define
class CreateBusinessAccessModel:
    """
    Attributes:
        suppress_notification_emails (Union[Unset, bool]):
        merge_existing_access (Union[Unset, bool]):
        access_type (Union[Unset, CreateBusinessAccessModelRelatedUserType]):
        employee_groups (Union[Unset, List['EmployeeGroupAccessModel']]):
        location_access (Union[Unset, List['LocationAccessModel']]):
        reports (Union[Unset, ReportAccessModel]):
        kiosk_access (Union[Unset, KioskAccessModel]):
        payroll_access (Union[Unset, PayrollAccessModel]):
        name (Union[Unset, str]):
        email (Union[Unset, str]):
    """

    suppress_notification_emails: Union[Unset, bool] = UNSET
    merge_existing_access: Union[Unset, bool] = UNSET
    access_type: Union[Unset, CreateBusinessAccessModelRelatedUserType] = UNSET
    employee_groups: Union[Unset, List["EmployeeGroupAccessModel"]] = UNSET
    location_access: Union[Unset, List["LocationAccessModel"]] = UNSET
    reports: Union[Unset, "ReportAccessModel"] = UNSET
    kiosk_access: Union[Unset, "KioskAccessModel"] = UNSET
    payroll_access: Union[Unset, "PayrollAccessModel"] = UNSET
    name: Union[Unset, str] = UNSET
    email: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        suppress_notification_emails = self.suppress_notification_emails

        merge_existing_access = self.merge_existing_access

        access_type: Union[Unset, str] = UNSET
        if not isinstance(self.access_type, Unset):
            access_type = self.access_type.value

        employee_groups: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.employee_groups, Unset):
            employee_groups = []
            for employee_groups_item_data in self.employee_groups:
                employee_groups_item = employee_groups_item_data.to_dict()
                employee_groups.append(employee_groups_item)

        location_access: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.location_access, Unset):
            location_access = []
            for location_access_item_data in self.location_access:
                location_access_item = location_access_item_data.to_dict()
                location_access.append(location_access_item)

        reports: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.reports, Unset):
            reports = self.reports.to_dict()

        kiosk_access: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.kiosk_access, Unset):
            kiosk_access = self.kiosk_access.to_dict()

        payroll_access: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.payroll_access, Unset):
            payroll_access = self.payroll_access.to_dict()

        name = self.name

        email = self.email

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if suppress_notification_emails is not UNSET:
            field_dict["suppressNotificationEmails"] = suppress_notification_emails
        if merge_existing_access is not UNSET:
            field_dict["mergeExistingAccess"] = merge_existing_access
        if access_type is not UNSET:
            field_dict["accessType"] = access_type
        if employee_groups is not UNSET:
            field_dict["employeeGroups"] = employee_groups
        if location_access is not UNSET:
            field_dict["locationAccess"] = location_access
        if reports is not UNSET:
            field_dict["reports"] = reports
        if kiosk_access is not UNSET:
            field_dict["kioskAccess"] = kiosk_access
        if payroll_access is not UNSET:
            field_dict["payrollAccess"] = payroll_access
        if name is not UNSET:
            field_dict["name"] = name
        if email is not UNSET:
            field_dict["email"] = email

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.employee_group_access_model import EmployeeGroupAccessModel
        from ..models.kiosk_access_model import KioskAccessModel
        from ..models.location_access_model import LocationAccessModel
        from ..models.payroll_access_model import PayrollAccessModel
        from ..models.report_access_model import ReportAccessModel

        d = src_dict.copy()
        suppress_notification_emails = d.pop("suppressNotificationEmails", UNSET)

        merge_existing_access = d.pop("mergeExistingAccess", UNSET)

        _access_type = d.pop("accessType", UNSET)
        access_type: Union[Unset, CreateBusinessAccessModelRelatedUserType]
        if isinstance(_access_type, Unset):
            access_type = UNSET
        else:
            access_type = CreateBusinessAccessModelRelatedUserType(_access_type)

        employee_groups = []
        _employee_groups = d.pop("employeeGroups", UNSET)
        for employee_groups_item_data in _employee_groups or []:
            employee_groups_item = EmployeeGroupAccessModel.from_dict(employee_groups_item_data)

            employee_groups.append(employee_groups_item)

        location_access = []
        _location_access = d.pop("locationAccess", UNSET)
        for location_access_item_data in _location_access or []:
            location_access_item = LocationAccessModel.from_dict(location_access_item_data)

            location_access.append(location_access_item)

        _reports = d.pop("reports", UNSET)
        reports: Union[Unset, ReportAccessModel]
        if isinstance(_reports, Unset):
            reports = UNSET
        else:
            reports = ReportAccessModel.from_dict(_reports)

        _kiosk_access = d.pop("kioskAccess", UNSET)
        kiosk_access: Union[Unset, KioskAccessModel]
        if isinstance(_kiosk_access, Unset):
            kiosk_access = UNSET
        else:
            kiosk_access = KioskAccessModel.from_dict(_kiosk_access)

        _payroll_access = d.pop("payrollAccess", UNSET)
        payroll_access: Union[Unset, PayrollAccessModel]
        if isinstance(_payroll_access, Unset):
            payroll_access = UNSET
        else:
            payroll_access = PayrollAccessModel.from_dict(_payroll_access)

        name = d.pop("name", UNSET)

        email = d.pop("email", UNSET)

        create_business_access_model = cls(
            suppress_notification_emails=suppress_notification_emails,
            merge_existing_access=merge_existing_access,
            access_type=access_type,
            employee_groups=employee_groups,
            location_access=location_access,
            reports=reports,
            kiosk_access=kiosk_access,
            payroll_access=payroll_access,
            name=name,
            email=email,
        )

        create_business_access_model.additional_properties = d
        return create_business_access_model

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
