import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.entitlement_feature_model import EntitlementFeatureModel


T = TypeVar("T", bound="EntitlementsModel")


@_attrs_define
class EntitlementsModel:
    """
    Attributes:
        plan_name (Union[Unset, str]):
        trial_expiry_date (Union[Unset, datetime.datetime]):
        features (Union[Unset, List['EntitlementFeatureModel']]):
    """

    plan_name: Union[Unset, str] = UNSET
    trial_expiry_date: Union[Unset, datetime.datetime] = UNSET
    features: Union[Unset, List["EntitlementFeatureModel"]] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        plan_name = self.plan_name

        trial_expiry_date: Union[Unset, str] = UNSET
        if not isinstance(self.trial_expiry_date, Unset):
            trial_expiry_date = self.trial_expiry_date.isoformat()

        features: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.features, Unset):
            features = []
            for features_item_data in self.features:
                features_item = features_item_data.to_dict()
                features.append(features_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if plan_name is not UNSET:
            field_dict["planName"] = plan_name
        if trial_expiry_date is not UNSET:
            field_dict["trialExpiryDate"] = trial_expiry_date
        if features is not UNSET:
            field_dict["features"] = features

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.entitlement_feature_model import EntitlementFeatureModel

        d = src_dict.copy()
        plan_name = d.pop("planName", UNSET)

        _trial_expiry_date = d.pop("trialExpiryDate", UNSET)
        trial_expiry_date: Union[Unset, datetime.datetime]
        if isinstance(_trial_expiry_date, Unset):
            trial_expiry_date = UNSET
        else:
            trial_expiry_date = isoparse(_trial_expiry_date)

        features = []
        _features = d.pop("features", UNSET)
        for features_item_data in _features or []:
            features_item = EntitlementFeatureModel.from_dict(features_item_data)

            features.append(features_item)

        entitlements_model = cls(
            plan_name=plan_name,
            trial_expiry_date=trial_expiry_date,
            features=features,
        )

        entitlements_model.additional_properties = d
        return entitlements_model

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
