import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.au_submit_timesheets_request_id_type import AuSubmitTimesheetsRequestIdType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.au_submit_timesheets_request_i_dictionary_string_i_list_1 import (
        AuSubmitTimesheetsRequestIDictionaryStringIList1,
    )


T = TypeVar("T", bound="AuSubmitTimesheetsRequest")


@_attrs_define
class AuSubmitTimesheetsRequest:
    """
    Attributes:
        from_date (Union[Unset, datetime.datetime]):
        to_date (Union[Unset, datetime.datetime]):
        replace_existing (Union[Unset, bool]):
        approved (Union[Unset, bool]):
        employee_id_type (Union[Unset, AuSubmitTimesheetsRequestIdType]):
        location_id_type (Union[Unset, AuSubmitTimesheetsRequestIdType]):
        work_type_id_type (Union[Unset, AuSubmitTimesheetsRequestIdType]):
        return_response (Union[Unset, bool]):
        timesheets (Union[Unset, AuSubmitTimesheetsRequestIDictionaryStringIList1]):
    """

    from_date: Union[Unset, datetime.datetime] = UNSET
    to_date: Union[Unset, datetime.datetime] = UNSET
    replace_existing: Union[Unset, bool] = UNSET
    approved: Union[Unset, bool] = UNSET
    employee_id_type: Union[Unset, AuSubmitTimesheetsRequestIdType] = UNSET
    location_id_type: Union[Unset, AuSubmitTimesheetsRequestIdType] = UNSET
    work_type_id_type: Union[Unset, AuSubmitTimesheetsRequestIdType] = UNSET
    return_response: Union[Unset, bool] = UNSET
    timesheets: Union[Unset, "AuSubmitTimesheetsRequestIDictionaryStringIList1"] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        from_date: Union[Unset, str] = UNSET
        if not isinstance(self.from_date, Unset):
            from_date = self.from_date.isoformat()

        to_date: Union[Unset, str] = UNSET
        if not isinstance(self.to_date, Unset):
            to_date = self.to_date.isoformat()

        replace_existing = self.replace_existing

        approved = self.approved

        employee_id_type: Union[Unset, str] = UNSET
        if not isinstance(self.employee_id_type, Unset):
            employee_id_type = self.employee_id_type.value

        location_id_type: Union[Unset, str] = UNSET
        if not isinstance(self.location_id_type, Unset):
            location_id_type = self.location_id_type.value

        work_type_id_type: Union[Unset, str] = UNSET
        if not isinstance(self.work_type_id_type, Unset):
            work_type_id_type = self.work_type_id_type.value

        return_response = self.return_response

        timesheets: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.timesheets, Unset):
            timesheets = self.timesheets.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if from_date is not UNSET:
            field_dict["fromDate"] = from_date
        if to_date is not UNSET:
            field_dict["toDate"] = to_date
        if replace_existing is not UNSET:
            field_dict["replaceExisting"] = replace_existing
        if approved is not UNSET:
            field_dict["approved"] = approved
        if employee_id_type is not UNSET:
            field_dict["employeeIdType"] = employee_id_type
        if location_id_type is not UNSET:
            field_dict["locationIdType"] = location_id_type
        if work_type_id_type is not UNSET:
            field_dict["workTypeIdType"] = work_type_id_type
        if return_response is not UNSET:
            field_dict["returnResponse"] = return_response
        if timesheets is not UNSET:
            field_dict["timesheets"] = timesheets

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.au_submit_timesheets_request_i_dictionary_string_i_list_1 import (
            AuSubmitTimesheetsRequestIDictionaryStringIList1,
        )

        d = src_dict.copy()
        _from_date = d.pop("fromDate", UNSET)
        from_date: Union[Unset, datetime.datetime]
        if isinstance(_from_date, Unset):
            from_date = UNSET
        else:
            from_date = isoparse(_from_date)

        _to_date = d.pop("toDate", UNSET)
        to_date: Union[Unset, datetime.datetime]
        if isinstance(_to_date, Unset):
            to_date = UNSET
        else:
            to_date = isoparse(_to_date)

        replace_existing = d.pop("replaceExisting", UNSET)

        approved = d.pop("approved", UNSET)

        _employee_id_type = d.pop("employeeIdType", UNSET)
        employee_id_type: Union[Unset, AuSubmitTimesheetsRequestIdType]
        if isinstance(_employee_id_type, Unset):
            employee_id_type = UNSET
        else:
            employee_id_type = AuSubmitTimesheetsRequestIdType(_employee_id_type)

        _location_id_type = d.pop("locationIdType", UNSET)
        location_id_type: Union[Unset, AuSubmitTimesheetsRequestIdType]
        if isinstance(_location_id_type, Unset):
            location_id_type = UNSET
        else:
            location_id_type = AuSubmitTimesheetsRequestIdType(_location_id_type)

        _work_type_id_type = d.pop("workTypeIdType", UNSET)
        work_type_id_type: Union[Unset, AuSubmitTimesheetsRequestIdType]
        if isinstance(_work_type_id_type, Unset):
            work_type_id_type = UNSET
        else:
            work_type_id_type = AuSubmitTimesheetsRequestIdType(_work_type_id_type)

        return_response = d.pop("returnResponse", UNSET)

        _timesheets = d.pop("timesheets", UNSET)
        timesheets: Union[Unset, AuSubmitTimesheetsRequestIDictionaryStringIList1]
        if isinstance(_timesheets, Unset):
            timesheets = UNSET
        else:
            timesheets = AuSubmitTimesheetsRequestIDictionaryStringIList1.from_dict(_timesheets)

        au_submit_timesheets_request = cls(
            from_date=from_date,
            to_date=to_date,
            replace_existing=replace_existing,
            approved=approved,
            employee_id_type=employee_id_type,
            location_id_type=location_id_type,
            work_type_id_type=work_type_id_type,
            return_response=return_response,
            timesheets=timesheets,
        )

        au_submit_timesheets_request.additional_properties = d
        return au_submit_timesheets_request

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
