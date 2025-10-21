from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="MLCSuperReportExportModel")


@_attrs_define
class MLCSuperReportExportModel:
    """
    Attributes:
        code (Union[Unset, str]):
        fund_code (Union[Unset, str]):
        spin (Union[Unset, str]):
        member_code (Union[Unset, str]):
        first_name (Union[Unset, str]):
        second_name (Union[Unset, str]):
        surname (Union[Unset, str]):
        title (Union[Unset, str]):
        gender (Union[Unset, str]):
        date_of_birth (Union[Unset, str]):
        address1 (Union[Unset, str]):
        address2 (Union[Unset, str]):
        suburb (Union[Unset, str]):
        state (Union[Unset, str]):
        postcode (Union[Unset, str]):
        telephone (Union[Unset, str]):
        mobile_phone (Union[Unset, str]):
        start_date (Union[Unset, str]):
        annual_salary (Union[Unset, str]):
        pay_group (Union[Unset, str]):
        benefit_category (Union[Unset, str]):
        end_date (Union[Unset, str]):
        super_guarantee (Union[Unset, str]):
        employer_additional (Union[Unset, str]):
        member_voluntary (Union[Unset, str]):
        salary_sacrifice (Union[Unset, str]):
        spouse_contribution (Union[Unset, str]):
        tax_file_number (Union[Unset, str]):
        employment_status (Union[Unset, str]):
    """

    code: Union[Unset, str] = UNSET
    fund_code: Union[Unset, str] = UNSET
    spin: Union[Unset, str] = UNSET
    member_code: Union[Unset, str] = UNSET
    first_name: Union[Unset, str] = UNSET
    second_name: Union[Unset, str] = UNSET
    surname: Union[Unset, str] = UNSET
    title: Union[Unset, str] = UNSET
    gender: Union[Unset, str] = UNSET
    date_of_birth: Union[Unset, str] = UNSET
    address1: Union[Unset, str] = UNSET
    address2: Union[Unset, str] = UNSET
    suburb: Union[Unset, str] = UNSET
    state: Union[Unset, str] = UNSET
    postcode: Union[Unset, str] = UNSET
    telephone: Union[Unset, str] = UNSET
    mobile_phone: Union[Unset, str] = UNSET
    start_date: Union[Unset, str] = UNSET
    annual_salary: Union[Unset, str] = UNSET
    pay_group: Union[Unset, str] = UNSET
    benefit_category: Union[Unset, str] = UNSET
    end_date: Union[Unset, str] = UNSET
    super_guarantee: Union[Unset, str] = UNSET
    employer_additional: Union[Unset, str] = UNSET
    member_voluntary: Union[Unset, str] = UNSET
    salary_sacrifice: Union[Unset, str] = UNSET
    spouse_contribution: Union[Unset, str] = UNSET
    tax_file_number: Union[Unset, str] = UNSET
    employment_status: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        code = self.code

        fund_code = self.fund_code

        spin = self.spin

        member_code = self.member_code

        first_name = self.first_name

        second_name = self.second_name

        surname = self.surname

        title = self.title

        gender = self.gender

        date_of_birth = self.date_of_birth

        address1 = self.address1

        address2 = self.address2

        suburb = self.suburb

        state = self.state

        postcode = self.postcode

        telephone = self.telephone

        mobile_phone = self.mobile_phone

        start_date = self.start_date

        annual_salary = self.annual_salary

        pay_group = self.pay_group

        benefit_category = self.benefit_category

        end_date = self.end_date

        super_guarantee = self.super_guarantee

        employer_additional = self.employer_additional

        member_voluntary = self.member_voluntary

        salary_sacrifice = self.salary_sacrifice

        spouse_contribution = self.spouse_contribution

        tax_file_number = self.tax_file_number

        employment_status = self.employment_status

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if code is not UNSET:
            field_dict["code"] = code
        if fund_code is not UNSET:
            field_dict["fundCode"] = fund_code
        if spin is not UNSET:
            field_dict["spin"] = spin
        if member_code is not UNSET:
            field_dict["memberCode"] = member_code
        if first_name is not UNSET:
            field_dict["firstName"] = first_name
        if second_name is not UNSET:
            field_dict["secondName"] = second_name
        if surname is not UNSET:
            field_dict["surname"] = surname
        if title is not UNSET:
            field_dict["title"] = title
        if gender is not UNSET:
            field_dict["gender"] = gender
        if date_of_birth is not UNSET:
            field_dict["dateOfBirth"] = date_of_birth
        if address1 is not UNSET:
            field_dict["address1"] = address1
        if address2 is not UNSET:
            field_dict["address2"] = address2
        if suburb is not UNSET:
            field_dict["suburb"] = suburb
        if state is not UNSET:
            field_dict["state"] = state
        if postcode is not UNSET:
            field_dict["postcode"] = postcode
        if telephone is not UNSET:
            field_dict["telephone"] = telephone
        if mobile_phone is not UNSET:
            field_dict["mobilePhone"] = mobile_phone
        if start_date is not UNSET:
            field_dict["startDate"] = start_date
        if annual_salary is not UNSET:
            field_dict["annualSalary"] = annual_salary
        if pay_group is not UNSET:
            field_dict["payGroup"] = pay_group
        if benefit_category is not UNSET:
            field_dict["benefitCategory"] = benefit_category
        if end_date is not UNSET:
            field_dict["endDate"] = end_date
        if super_guarantee is not UNSET:
            field_dict["superGuarantee"] = super_guarantee
        if employer_additional is not UNSET:
            field_dict["employerAdditional"] = employer_additional
        if member_voluntary is not UNSET:
            field_dict["memberVoluntary"] = member_voluntary
        if salary_sacrifice is not UNSET:
            field_dict["salarySacrifice"] = salary_sacrifice
        if spouse_contribution is not UNSET:
            field_dict["spouseContribution"] = spouse_contribution
        if tax_file_number is not UNSET:
            field_dict["taxFileNumber"] = tax_file_number
        if employment_status is not UNSET:
            field_dict["employmentStatus"] = employment_status

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        code = d.pop("code", UNSET)

        fund_code = d.pop("fundCode", UNSET)

        spin = d.pop("spin", UNSET)

        member_code = d.pop("memberCode", UNSET)

        first_name = d.pop("firstName", UNSET)

        second_name = d.pop("secondName", UNSET)

        surname = d.pop("surname", UNSET)

        title = d.pop("title", UNSET)

        gender = d.pop("gender", UNSET)

        date_of_birth = d.pop("dateOfBirth", UNSET)

        address1 = d.pop("address1", UNSET)

        address2 = d.pop("address2", UNSET)

        suburb = d.pop("suburb", UNSET)

        state = d.pop("state", UNSET)

        postcode = d.pop("postcode", UNSET)

        telephone = d.pop("telephone", UNSET)

        mobile_phone = d.pop("mobilePhone", UNSET)

        start_date = d.pop("startDate", UNSET)

        annual_salary = d.pop("annualSalary", UNSET)

        pay_group = d.pop("payGroup", UNSET)

        benefit_category = d.pop("benefitCategory", UNSET)

        end_date = d.pop("endDate", UNSET)

        super_guarantee = d.pop("superGuarantee", UNSET)

        employer_additional = d.pop("employerAdditional", UNSET)

        member_voluntary = d.pop("memberVoluntary", UNSET)

        salary_sacrifice = d.pop("salarySacrifice", UNSET)

        spouse_contribution = d.pop("spouseContribution", UNSET)

        tax_file_number = d.pop("taxFileNumber", UNSET)

        employment_status = d.pop("employmentStatus", UNSET)

        mlc_super_report_export_model = cls(
            code=code,
            fund_code=fund_code,
            spin=spin,
            member_code=member_code,
            first_name=first_name,
            second_name=second_name,
            surname=surname,
            title=title,
            gender=gender,
            date_of_birth=date_of_birth,
            address1=address1,
            address2=address2,
            suburb=suburb,
            state=state,
            postcode=postcode,
            telephone=telephone,
            mobile_phone=mobile_phone,
            start_date=start_date,
            annual_salary=annual_salary,
            pay_group=pay_group,
            benefit_category=benefit_category,
            end_date=end_date,
            super_guarantee=super_guarantee,
            employer_additional=employer_additional,
            member_voluntary=member_voluntary,
            salary_sacrifice=salary_sacrifice,
            spouse_contribution=spouse_contribution,
            tax_file_number=tax_file_number,
            employment_status=employment_status,
        )

        mlc_super_report_export_model.additional_properties = d
        return mlc_super_report_export_model

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
