from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.au_chart_of_accounts_group_model import AuChartOfAccountsGroupModel
    from ..models.au_chart_of_accounts_location_group_model import AuChartOfAccountsLocationGroupModel


T = TypeVar("T", bound="AuChartOfAccountsModel")


@_attrs_define
class AuChartOfAccountsModel:
    """
    Attributes:
        complete (Union[Unset, bool]):
        chartof_accounts (Union[Unset, AuChartOfAccountsGroupModel]):
        location_specific_chart_of_accounts (Union[Unset, List['AuChartOfAccountsLocationGroupModel']]):
    """

    complete: Union[Unset, bool] = UNSET
    chartof_accounts: Union[Unset, "AuChartOfAccountsGroupModel"] = UNSET
    location_specific_chart_of_accounts: Union[Unset, List["AuChartOfAccountsLocationGroupModel"]] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        complete = self.complete

        chartof_accounts: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.chartof_accounts, Unset):
            chartof_accounts = self.chartof_accounts.to_dict()

        location_specific_chart_of_accounts: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.location_specific_chart_of_accounts, Unset):
            location_specific_chart_of_accounts = []
            for location_specific_chart_of_accounts_item_data in self.location_specific_chart_of_accounts:
                location_specific_chart_of_accounts_item = location_specific_chart_of_accounts_item_data.to_dict()
                location_specific_chart_of_accounts.append(location_specific_chart_of_accounts_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if complete is not UNSET:
            field_dict["complete"] = complete
        if chartof_accounts is not UNSET:
            field_dict["chartofAccounts"] = chartof_accounts
        if location_specific_chart_of_accounts is not UNSET:
            field_dict["locationSpecificChartOfAccounts"] = location_specific_chart_of_accounts

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.au_chart_of_accounts_group_model import AuChartOfAccountsGroupModel
        from ..models.au_chart_of_accounts_location_group_model import AuChartOfAccountsLocationGroupModel

        d = src_dict.copy()
        complete = d.pop("complete", UNSET)

        _chartof_accounts = d.pop("chartofAccounts", UNSET)
        chartof_accounts: Union[Unset, AuChartOfAccountsGroupModel]
        if isinstance(_chartof_accounts, Unset):
            chartof_accounts = UNSET
        else:
            chartof_accounts = AuChartOfAccountsGroupModel.from_dict(_chartof_accounts)

        location_specific_chart_of_accounts = []
        _location_specific_chart_of_accounts = d.pop("locationSpecificChartOfAccounts", UNSET)
        for location_specific_chart_of_accounts_item_data in _location_specific_chart_of_accounts or []:
            location_specific_chart_of_accounts_item = AuChartOfAccountsLocationGroupModel.from_dict(
                location_specific_chart_of_accounts_item_data
            )

            location_specific_chart_of_accounts.append(location_specific_chart_of_accounts_item)

        au_chart_of_accounts_model = cls(
            complete=complete,
            chartof_accounts=chartof_accounts,
            location_specific_chart_of_accounts=location_specific_chart_of_accounts,
        )

        au_chart_of_accounts_model.additional_properties = d
        return au_chart_of_accounts_model

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
