from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.au_journal_item_response_journal_item_type import AuJournalItemResponseJournalItemType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.au_journal_item_response_i_dictionary_string_i_list_1 import (
        AuJournalItemResponseIDictionaryStringIList1,
    )


T = TypeVar("T", bound="AuJournalItemResponse")


@_attrs_define
class AuJournalItemResponse:
    """
    Attributes:
        journal_item_type (Union[Unset, AuJournalItemResponseJournalItemType]):
        external_account_reference_id (Union[Unset, str]):
        units (Union[Unset, float]):
        amount (Union[Unset, float]):
        amount_unrounded (Union[Unset, float]):
        reference (Union[Unset, str]):
        tax_code (Union[Unset, str]):
        account_code (Union[Unset, str]):
        account_name (Union[Unset, str]):
        details (Union[Unset, str]):
        location (Union[Unset, str]):
        is_credit (Union[Unset, bool]):
        is_debit (Union[Unset, bool]):
        location_external_reference_id (Union[Unset, str]):
        reporting_dimension_value_ids (Union[Unset, List[int]]): Nullable</p><p><i>Note:</i> Only applicable to
            businesses where the Dimensions feature is enabled.</p><p>Specify an array of dimension value ids (normally only
            one-per dimension) eg [1,3,7].</p><p>If you prefer to specify dimension values by name, use the
            ReportingDimensionValueNames field instead.</p><p>If this field is used, ReportingDimensionValueNames will be
            ignored (the Ids take precedence)
        reporting_dimension_value_names (Union[Unset, AuJournalItemResponseIDictionaryStringIList1]):
            Nullable</p><p><i>Note:</i> Only applicable to businesses where the Dimensions feature is enabled.</p><p>Specify
            an object with dimension names and for each one, specify an array of associated value names (normally one-per
            dimension) eg { "Department": ["Accounting"], "Job Code": ["JC1"] }.</p><p>If you prefer to specify dimension
            values directly by Id, use the ReportingDimensionValueIds field instead.</p><p>If ReportingDimensionValueIds is
            used, ReportingDimensionValueNames will be ignored (the Ids take precedence)
    """

    journal_item_type: Union[Unset, AuJournalItemResponseJournalItemType] = UNSET
    external_account_reference_id: Union[Unset, str] = UNSET
    units: Union[Unset, float] = UNSET
    amount: Union[Unset, float] = UNSET
    amount_unrounded: Union[Unset, float] = UNSET
    reference: Union[Unset, str] = UNSET
    tax_code: Union[Unset, str] = UNSET
    account_code: Union[Unset, str] = UNSET
    account_name: Union[Unset, str] = UNSET
    details: Union[Unset, str] = UNSET
    location: Union[Unset, str] = UNSET
    is_credit: Union[Unset, bool] = UNSET
    is_debit: Union[Unset, bool] = UNSET
    location_external_reference_id: Union[Unset, str] = UNSET
    reporting_dimension_value_ids: Union[Unset, List[int]] = UNSET
    reporting_dimension_value_names: Union[Unset, "AuJournalItemResponseIDictionaryStringIList1"] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        journal_item_type: Union[Unset, str] = UNSET
        if not isinstance(self.journal_item_type, Unset):
            journal_item_type = self.journal_item_type.value

        external_account_reference_id = self.external_account_reference_id

        units = self.units

        amount = self.amount

        amount_unrounded = self.amount_unrounded

        reference = self.reference

        tax_code = self.tax_code

        account_code = self.account_code

        account_name = self.account_name

        details = self.details

        location = self.location

        is_credit = self.is_credit

        is_debit = self.is_debit

        location_external_reference_id = self.location_external_reference_id

        reporting_dimension_value_ids: Union[Unset, List[int]] = UNSET
        if not isinstance(self.reporting_dimension_value_ids, Unset):
            reporting_dimension_value_ids = self.reporting_dimension_value_ids

        reporting_dimension_value_names: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.reporting_dimension_value_names, Unset):
            reporting_dimension_value_names = self.reporting_dimension_value_names.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if journal_item_type is not UNSET:
            field_dict["journalItemType"] = journal_item_type
        if external_account_reference_id is not UNSET:
            field_dict["externalAccountReferenceId"] = external_account_reference_id
        if units is not UNSET:
            field_dict["units"] = units
        if amount is not UNSET:
            field_dict["amount"] = amount
        if amount_unrounded is not UNSET:
            field_dict["amountUnrounded"] = amount_unrounded
        if reference is not UNSET:
            field_dict["reference"] = reference
        if tax_code is not UNSET:
            field_dict["taxCode"] = tax_code
        if account_code is not UNSET:
            field_dict["accountCode"] = account_code
        if account_name is not UNSET:
            field_dict["accountName"] = account_name
        if details is not UNSET:
            field_dict["details"] = details
        if location is not UNSET:
            field_dict["location"] = location
        if is_credit is not UNSET:
            field_dict["isCredit"] = is_credit
        if is_debit is not UNSET:
            field_dict["isDebit"] = is_debit
        if location_external_reference_id is not UNSET:
            field_dict["locationExternalReferenceId"] = location_external_reference_id
        if reporting_dimension_value_ids is not UNSET:
            field_dict["reportingDimensionValueIds"] = reporting_dimension_value_ids
        if reporting_dimension_value_names is not UNSET:
            field_dict["reportingDimensionValueNames"] = reporting_dimension_value_names

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.au_journal_item_response_i_dictionary_string_i_list_1 import (
            AuJournalItemResponseIDictionaryStringIList1,
        )

        d = src_dict.copy()
        _journal_item_type = d.pop("journalItemType", UNSET)
        journal_item_type: Union[Unset, AuJournalItemResponseJournalItemType]
        if isinstance(_journal_item_type, Unset):
            journal_item_type = UNSET
        else:
            journal_item_type = AuJournalItemResponseJournalItemType(_journal_item_type)

        external_account_reference_id = d.pop("externalAccountReferenceId", UNSET)

        units = d.pop("units", UNSET)

        amount = d.pop("amount", UNSET)

        amount_unrounded = d.pop("amountUnrounded", UNSET)

        reference = d.pop("reference", UNSET)

        tax_code = d.pop("taxCode", UNSET)

        account_code = d.pop("accountCode", UNSET)

        account_name = d.pop("accountName", UNSET)

        details = d.pop("details", UNSET)

        location = d.pop("location", UNSET)

        is_credit = d.pop("isCredit", UNSET)

        is_debit = d.pop("isDebit", UNSET)

        location_external_reference_id = d.pop("locationExternalReferenceId", UNSET)

        reporting_dimension_value_ids = cast(List[int], d.pop("reportingDimensionValueIds", UNSET))

        _reporting_dimension_value_names = d.pop("reportingDimensionValueNames", UNSET)
        reporting_dimension_value_names: Union[Unset, AuJournalItemResponseIDictionaryStringIList1]
        if isinstance(_reporting_dimension_value_names, Unset):
            reporting_dimension_value_names = UNSET
        else:
            reporting_dimension_value_names = AuJournalItemResponseIDictionaryStringIList1.from_dict(
                _reporting_dimension_value_names
            )

        au_journal_item_response = cls(
            journal_item_type=journal_item_type,
            external_account_reference_id=external_account_reference_id,
            units=units,
            amount=amount,
            amount_unrounded=amount_unrounded,
            reference=reference,
            tax_code=tax_code,
            account_code=account_code,
            account_name=account_name,
            details=details,
            location=location,
            is_credit=is_credit,
            is_debit=is_debit,
            location_external_reference_id=location_external_reference_id,
            reporting_dimension_value_ids=reporting_dimension_value_ids,
            reporting_dimension_value_names=reporting_dimension_value_names,
        )

        au_journal_item_response.additional_properties = d
        return au_journal_item_response

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
