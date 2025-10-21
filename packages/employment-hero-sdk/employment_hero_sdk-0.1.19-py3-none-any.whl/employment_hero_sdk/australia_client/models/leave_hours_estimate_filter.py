import datetime
from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="LeaveHoursEstimateFilter")


@_attrs_define
class LeaveHoursEstimateFilter:
    """
    Attributes:
        from_date (datetime.datetime): Required
        to_date (datetime.datetime): Required
        leave_category_id (Union[Unset, int]):
    """

    from_date: datetime.datetime
    to_date: datetime.datetime
    leave_category_id: Union[Unset, int] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        from_date = self.from_date.isoformat()

        to_date = self.to_date.isoformat()

        leave_category_id = self.leave_category_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "fromDate": from_date,
                "toDate": to_date,
            }
        )
        if leave_category_id is not UNSET:
            field_dict["leaveCategoryId"] = leave_category_id

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        from_date = isoparse(d.pop("fromDate"))

        to_date = isoparse(d.pop("toDate"))

        leave_category_id = d.pop("leaveCategoryId", UNSET)

        leave_hours_estimate_filter = cls(
            from_date=from_date,
            to_date=to_date,
            leave_category_id=leave_category_id,
        )

        leave_hours_estimate_filter.additional_properties = d
        return leave_hours_estimate_filter

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
