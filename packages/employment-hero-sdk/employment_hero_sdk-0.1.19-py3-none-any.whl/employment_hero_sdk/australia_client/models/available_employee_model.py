from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.white_label_branding_model import WhiteLabelBrandingModel


T = TypeVar("T", bound="AvailableEmployeeModel")


@_attrs_define
class AvailableEmployeeModel:
    """
    Attributes:
        id (Union[Unset, int]):
        name (Union[Unset, str]):
        business_id (Union[Unset, int]):
        business_name (Union[Unset, str]):
        job_title (Union[Unset, str]):
        has_profile_image (Union[Unset, bool]):
        branding (Union[Unset, WhiteLabelBrandingModel]):
        default_location_id (Union[Unset, int]):
        profile_image_url (Union[Unset, str]):
        region (Union[Unset, str]):
        is_terminated (Union[Unset, bool]):
    """

    id: Union[Unset, int] = UNSET
    name: Union[Unset, str] = UNSET
    business_id: Union[Unset, int] = UNSET
    business_name: Union[Unset, str] = UNSET
    job_title: Union[Unset, str] = UNSET
    has_profile_image: Union[Unset, bool] = UNSET
    branding: Union[Unset, "WhiteLabelBrandingModel"] = UNSET
    default_location_id: Union[Unset, int] = UNSET
    profile_image_url: Union[Unset, str] = UNSET
    region: Union[Unset, str] = UNSET
    is_terminated: Union[Unset, bool] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        id = self.id

        name = self.name

        business_id = self.business_id

        business_name = self.business_name

        job_title = self.job_title

        has_profile_image = self.has_profile_image

        branding: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.branding, Unset):
            branding = self.branding.to_dict()

        default_location_id = self.default_location_id

        profile_image_url = self.profile_image_url

        region = self.region

        is_terminated = self.is_terminated

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if name is not UNSET:
            field_dict["name"] = name
        if business_id is not UNSET:
            field_dict["businessId"] = business_id
        if business_name is not UNSET:
            field_dict["businessName"] = business_name
        if job_title is not UNSET:
            field_dict["jobTitle"] = job_title
        if has_profile_image is not UNSET:
            field_dict["hasProfileImage"] = has_profile_image
        if branding is not UNSET:
            field_dict["branding"] = branding
        if default_location_id is not UNSET:
            field_dict["defaultLocationId"] = default_location_id
        if profile_image_url is not UNSET:
            field_dict["profileImageUrl"] = profile_image_url
        if region is not UNSET:
            field_dict["region"] = region
        if is_terminated is not UNSET:
            field_dict["isTerminated"] = is_terminated

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.white_label_branding_model import WhiteLabelBrandingModel

        d = src_dict.copy()
        id = d.pop("id", UNSET)

        name = d.pop("name", UNSET)

        business_id = d.pop("businessId", UNSET)

        business_name = d.pop("businessName", UNSET)

        job_title = d.pop("jobTitle", UNSET)

        has_profile_image = d.pop("hasProfileImage", UNSET)

        _branding = d.pop("branding", UNSET)
        branding: Union[Unset, WhiteLabelBrandingModel]
        if isinstance(_branding, Unset):
            branding = UNSET
        else:
            branding = WhiteLabelBrandingModel.from_dict(_branding)

        default_location_id = d.pop("defaultLocationId", UNSET)

        profile_image_url = d.pop("profileImageUrl", UNSET)

        region = d.pop("region", UNSET)

        is_terminated = d.pop("isTerminated", UNSET)

        available_employee_model = cls(
            id=id,
            name=name,
            business_id=business_id,
            business_name=business_name,
            job_title=job_title,
            has_profile_image=has_profile_image,
            branding=branding,
            default_location_id=default_location_id,
            profile_image_url=profile_image_url,
            region=region,
            is_terminated=is_terminated,
        )

        available_employee_model.additional_properties = d
        return available_employee_model

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
