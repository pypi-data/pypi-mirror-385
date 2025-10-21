from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="WhiteLabelBrandingModel")


@_attrs_define
class WhiteLabelBrandingModel:
    """
    Attributes:
        logo_url (Union[Unset, str]):
        background_image_url (Union[Unset, str]):
        background_colour (Union[Unset, str]):
        text_colour (Union[Unset, str]):
        text_hover_colour (Union[Unset, str]):
        text_secondary_colour (Union[Unset, str]):
        dark_mode_logo_url (Union[Unset, str]):
        dark_mode_background_colour (Union[Unset, str]):
        dark_mode_text_colour (Union[Unset, str]):
        dark_mode_text_secondary_colour (Union[Unset, str]):
    """

    logo_url: Union[Unset, str] = UNSET
    background_image_url: Union[Unset, str] = UNSET
    background_colour: Union[Unset, str] = UNSET
    text_colour: Union[Unset, str] = UNSET
    text_hover_colour: Union[Unset, str] = UNSET
    text_secondary_colour: Union[Unset, str] = UNSET
    dark_mode_logo_url: Union[Unset, str] = UNSET
    dark_mode_background_colour: Union[Unset, str] = UNSET
    dark_mode_text_colour: Union[Unset, str] = UNSET
    dark_mode_text_secondary_colour: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        logo_url = self.logo_url

        background_image_url = self.background_image_url

        background_colour = self.background_colour

        text_colour = self.text_colour

        text_hover_colour = self.text_hover_colour

        text_secondary_colour = self.text_secondary_colour

        dark_mode_logo_url = self.dark_mode_logo_url

        dark_mode_background_colour = self.dark_mode_background_colour

        dark_mode_text_colour = self.dark_mode_text_colour

        dark_mode_text_secondary_colour = self.dark_mode_text_secondary_colour

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if logo_url is not UNSET:
            field_dict["logoUrl"] = logo_url
        if background_image_url is not UNSET:
            field_dict["backgroundImageUrl"] = background_image_url
        if background_colour is not UNSET:
            field_dict["backgroundColour"] = background_colour
        if text_colour is not UNSET:
            field_dict["textColour"] = text_colour
        if text_hover_colour is not UNSET:
            field_dict["textHoverColour"] = text_hover_colour
        if text_secondary_colour is not UNSET:
            field_dict["textSecondaryColour"] = text_secondary_colour
        if dark_mode_logo_url is not UNSET:
            field_dict["darkModeLogoUrl"] = dark_mode_logo_url
        if dark_mode_background_colour is not UNSET:
            field_dict["darkModeBackgroundColour"] = dark_mode_background_colour
        if dark_mode_text_colour is not UNSET:
            field_dict["darkModeTextColour"] = dark_mode_text_colour
        if dark_mode_text_secondary_colour is not UNSET:
            field_dict["darkModeTextSecondaryColour"] = dark_mode_text_secondary_colour

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        logo_url = d.pop("logoUrl", UNSET)

        background_image_url = d.pop("backgroundImageUrl", UNSET)

        background_colour = d.pop("backgroundColour", UNSET)

        text_colour = d.pop("textColour", UNSET)

        text_hover_colour = d.pop("textHoverColour", UNSET)

        text_secondary_colour = d.pop("textSecondaryColour", UNSET)

        dark_mode_logo_url = d.pop("darkModeLogoUrl", UNSET)

        dark_mode_background_colour = d.pop("darkModeBackgroundColour", UNSET)

        dark_mode_text_colour = d.pop("darkModeTextColour", UNSET)

        dark_mode_text_secondary_colour = d.pop("darkModeTextSecondaryColour", UNSET)

        white_label_branding_model = cls(
            logo_url=logo_url,
            background_image_url=background_image_url,
            background_colour=background_colour,
            text_colour=text_colour,
            text_hover_colour=text_hover_colour,
            text_secondary_colour=text_secondary_colour,
            dark_mode_logo_url=dark_mode_logo_url,
            dark_mode_background_colour=dark_mode_background_colour,
            dark_mode_text_colour=dark_mode_text_colour,
            dark_mode_text_secondary_colour=dark_mode_text_secondary_colour,
        )

        white_label_branding_model.additional_properties = d
        return white_label_branding_model

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
