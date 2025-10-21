import datetime
from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="PayRunTotalModel")


@_attrs_define
class PayRunTotalModel:
    """
    Attributes:
        id (Union[Unset, int]):
        total_hours (Union[Unset, float]):
        gross_earnings (Union[Unset, float]):
        pre_tax_deductions (Union[Unset, float]):
        taxable_earnings (Union[Unset, float]):
        post_tax_deductions (Union[Unset, float]):
        net_earnings (Union[Unset, float]):
        total_employee_expenses (Union[Unset, float]):
        total_employer_liabilities (Union[Unset, float]):
        is_published (Union[Unset, bool]):
        pay_run_id (Union[Unset, int]):
        notes (Union[Unset, str]):
        notation (Union[Unset, str]):
        payg_withheld (Union[Unset, float]):
        sfss_withheld (Union[Unset, float]):
        help_withheld (Union[Unset, float]):
        super_contribution (Union[Unset, float]):
        employer_contribution (Union[Unset, float]):
        kiwi_saver_employee_contribution (Union[Unset, float]):
        kiwi_saver_employer_contribution (Union[Unset, float]):
        esct_contribution (Union[Unset, float]):
        student_loan_amount (Union[Unset, float]):
        post_grad_loan_amount (Union[Unset, float]):
        student_loan_additional_mandatory_amount (Union[Unset, float]):
        student_loan_additional_voluntary_amount (Union[Unset, float]):
        acc_levy_amount (Union[Unset, float]):
        cpf_employer_contribution_amount (Union[Unset, float]):
        cpf_employee_contribution_amount (Union[Unset, float]):
        employer_voluntary_cpf_amount (Union[Unset, float]):
        employer_voluntary_medi_save_amount (Union[Unset, float]):
        sdl_contribution_amount (Union[Unset, float]):
        employer_pension_contribution (Union[Unset, float]):
        employee_pension_contribution (Union[Unset, float]):
        employee_national_insurance_contribution (Union[Unset, float]):
        employer_national_insurance_contribution (Union[Unset, float]):
        employee_pensionable_earnings (Union[Unset, float]):
        employer_pensionable_earnings (Union[Unset, float]):
        termination_payment_ni_exempt (Union[Unset, float]):
        termination_payment_employer_ni (Union[Unset, float]):
        nic_class_1a (Union[Unset, float]):
        enrolled_in_pension_scheme (Union[Unset, bool]):
        deferral_date (Union[Unset, datetime.datetime]):
        bik_taxable_amount (Union[Unset, float]):
        bik_tax_exempt_amount (Union[Unset, float]):
        cp_38_amount (Union[Unset, float]):
        pcb_borne_by_employer_amount (Union[Unset, float]):
        epf_employer_amount (Union[Unset, float]):
        epf_employee_amount (Union[Unset, float]):
        eis_employer_amount (Union[Unset, float]):
        eis_employee_amount (Union[Unset, float]):
        socso_employer_amount (Union[Unset, float]):
        socso_employee_amount (Union[Unset, float]):
        hrdf_amount (Union[Unset, float]):
    """

    id: Union[Unset, int] = UNSET
    total_hours: Union[Unset, float] = UNSET
    gross_earnings: Union[Unset, float] = UNSET
    pre_tax_deductions: Union[Unset, float] = UNSET
    taxable_earnings: Union[Unset, float] = UNSET
    post_tax_deductions: Union[Unset, float] = UNSET
    net_earnings: Union[Unset, float] = UNSET
    total_employee_expenses: Union[Unset, float] = UNSET
    total_employer_liabilities: Union[Unset, float] = UNSET
    is_published: Union[Unset, bool] = UNSET
    pay_run_id: Union[Unset, int] = UNSET
    notes: Union[Unset, str] = UNSET
    notation: Union[Unset, str] = UNSET
    payg_withheld: Union[Unset, float] = UNSET
    sfss_withheld: Union[Unset, float] = UNSET
    help_withheld: Union[Unset, float] = UNSET
    super_contribution: Union[Unset, float] = UNSET
    employer_contribution: Union[Unset, float] = UNSET
    kiwi_saver_employee_contribution: Union[Unset, float] = UNSET
    kiwi_saver_employer_contribution: Union[Unset, float] = UNSET
    esct_contribution: Union[Unset, float] = UNSET
    student_loan_amount: Union[Unset, float] = UNSET
    post_grad_loan_amount: Union[Unset, float] = UNSET
    student_loan_additional_mandatory_amount: Union[Unset, float] = UNSET
    student_loan_additional_voluntary_amount: Union[Unset, float] = UNSET
    acc_levy_amount: Union[Unset, float] = UNSET
    cpf_employer_contribution_amount: Union[Unset, float] = UNSET
    cpf_employee_contribution_amount: Union[Unset, float] = UNSET
    employer_voluntary_cpf_amount: Union[Unset, float] = UNSET
    employer_voluntary_medi_save_amount: Union[Unset, float] = UNSET
    sdl_contribution_amount: Union[Unset, float] = UNSET
    employer_pension_contribution: Union[Unset, float] = UNSET
    employee_pension_contribution: Union[Unset, float] = UNSET
    employee_national_insurance_contribution: Union[Unset, float] = UNSET
    employer_national_insurance_contribution: Union[Unset, float] = UNSET
    employee_pensionable_earnings: Union[Unset, float] = UNSET
    employer_pensionable_earnings: Union[Unset, float] = UNSET
    termination_payment_ni_exempt: Union[Unset, float] = UNSET
    termination_payment_employer_ni: Union[Unset, float] = UNSET
    nic_class_1a: Union[Unset, float] = UNSET
    enrolled_in_pension_scheme: Union[Unset, bool] = UNSET
    deferral_date: Union[Unset, datetime.datetime] = UNSET
    bik_taxable_amount: Union[Unset, float] = UNSET
    bik_tax_exempt_amount: Union[Unset, float] = UNSET
    cp_38_amount: Union[Unset, float] = UNSET
    pcb_borne_by_employer_amount: Union[Unset, float] = UNSET
    epf_employer_amount: Union[Unset, float] = UNSET
    epf_employee_amount: Union[Unset, float] = UNSET
    eis_employer_amount: Union[Unset, float] = UNSET
    eis_employee_amount: Union[Unset, float] = UNSET
    socso_employer_amount: Union[Unset, float] = UNSET
    socso_employee_amount: Union[Unset, float] = UNSET
    hrdf_amount: Union[Unset, float] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        id = self.id

        total_hours = self.total_hours

        gross_earnings = self.gross_earnings

        pre_tax_deductions = self.pre_tax_deductions

        taxable_earnings = self.taxable_earnings

        post_tax_deductions = self.post_tax_deductions

        net_earnings = self.net_earnings

        total_employee_expenses = self.total_employee_expenses

        total_employer_liabilities = self.total_employer_liabilities

        is_published = self.is_published

        pay_run_id = self.pay_run_id

        notes = self.notes

        notation = self.notation

        payg_withheld = self.payg_withheld

        sfss_withheld = self.sfss_withheld

        help_withheld = self.help_withheld

        super_contribution = self.super_contribution

        employer_contribution = self.employer_contribution

        kiwi_saver_employee_contribution = self.kiwi_saver_employee_contribution

        kiwi_saver_employer_contribution = self.kiwi_saver_employer_contribution

        esct_contribution = self.esct_contribution

        student_loan_amount = self.student_loan_amount

        post_grad_loan_amount = self.post_grad_loan_amount

        student_loan_additional_mandatory_amount = self.student_loan_additional_mandatory_amount

        student_loan_additional_voluntary_amount = self.student_loan_additional_voluntary_amount

        acc_levy_amount = self.acc_levy_amount

        cpf_employer_contribution_amount = self.cpf_employer_contribution_amount

        cpf_employee_contribution_amount = self.cpf_employee_contribution_amount

        employer_voluntary_cpf_amount = self.employer_voluntary_cpf_amount

        employer_voluntary_medi_save_amount = self.employer_voluntary_medi_save_amount

        sdl_contribution_amount = self.sdl_contribution_amount

        employer_pension_contribution = self.employer_pension_contribution

        employee_pension_contribution = self.employee_pension_contribution

        employee_national_insurance_contribution = self.employee_national_insurance_contribution

        employer_national_insurance_contribution = self.employer_national_insurance_contribution

        employee_pensionable_earnings = self.employee_pensionable_earnings

        employer_pensionable_earnings = self.employer_pensionable_earnings

        termination_payment_ni_exempt = self.termination_payment_ni_exempt

        termination_payment_employer_ni = self.termination_payment_employer_ni

        nic_class_1a = self.nic_class_1a

        enrolled_in_pension_scheme = self.enrolled_in_pension_scheme

        deferral_date: Union[Unset, str] = UNSET
        if not isinstance(self.deferral_date, Unset):
            deferral_date = self.deferral_date.isoformat()

        bik_taxable_amount = self.bik_taxable_amount

        bik_tax_exempt_amount = self.bik_tax_exempt_amount

        cp_38_amount = self.cp_38_amount

        pcb_borne_by_employer_amount = self.pcb_borne_by_employer_amount

        epf_employer_amount = self.epf_employer_amount

        epf_employee_amount = self.epf_employee_amount

        eis_employer_amount = self.eis_employer_amount

        eis_employee_amount = self.eis_employee_amount

        socso_employer_amount = self.socso_employer_amount

        socso_employee_amount = self.socso_employee_amount

        hrdf_amount = self.hrdf_amount

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if total_hours is not UNSET:
            field_dict["totalHours"] = total_hours
        if gross_earnings is not UNSET:
            field_dict["grossEarnings"] = gross_earnings
        if pre_tax_deductions is not UNSET:
            field_dict["preTaxDeductions"] = pre_tax_deductions
        if taxable_earnings is not UNSET:
            field_dict["taxableEarnings"] = taxable_earnings
        if post_tax_deductions is not UNSET:
            field_dict["postTaxDeductions"] = post_tax_deductions
        if net_earnings is not UNSET:
            field_dict["netEarnings"] = net_earnings
        if total_employee_expenses is not UNSET:
            field_dict["totalEmployeeExpenses"] = total_employee_expenses
        if total_employer_liabilities is not UNSET:
            field_dict["totalEmployerLiabilities"] = total_employer_liabilities
        if is_published is not UNSET:
            field_dict["isPublished"] = is_published
        if pay_run_id is not UNSET:
            field_dict["payRunId"] = pay_run_id
        if notes is not UNSET:
            field_dict["notes"] = notes
        if notation is not UNSET:
            field_dict["notation"] = notation
        if payg_withheld is not UNSET:
            field_dict["paygWithheld"] = payg_withheld
        if sfss_withheld is not UNSET:
            field_dict["sfssWithheld"] = sfss_withheld
        if help_withheld is not UNSET:
            field_dict["helpWithheld"] = help_withheld
        if super_contribution is not UNSET:
            field_dict["superContribution"] = super_contribution
        if employer_contribution is not UNSET:
            field_dict["employerContribution"] = employer_contribution
        if kiwi_saver_employee_contribution is not UNSET:
            field_dict["kiwiSaverEmployeeContribution"] = kiwi_saver_employee_contribution
        if kiwi_saver_employer_contribution is not UNSET:
            field_dict["kiwiSaverEmployerContribution"] = kiwi_saver_employer_contribution
        if esct_contribution is not UNSET:
            field_dict["esctContribution"] = esct_contribution
        if student_loan_amount is not UNSET:
            field_dict["studentLoanAmount"] = student_loan_amount
        if post_grad_loan_amount is not UNSET:
            field_dict["postGradLoanAmount"] = post_grad_loan_amount
        if student_loan_additional_mandatory_amount is not UNSET:
            field_dict["studentLoanAdditionalMandatoryAmount"] = student_loan_additional_mandatory_amount
        if student_loan_additional_voluntary_amount is not UNSET:
            field_dict["studentLoanAdditionalVoluntaryAmount"] = student_loan_additional_voluntary_amount
        if acc_levy_amount is not UNSET:
            field_dict["accLevyAmount"] = acc_levy_amount
        if cpf_employer_contribution_amount is not UNSET:
            field_dict["cpfEmployerContributionAmount"] = cpf_employer_contribution_amount
        if cpf_employee_contribution_amount is not UNSET:
            field_dict["cpfEmployeeContributionAmount"] = cpf_employee_contribution_amount
        if employer_voluntary_cpf_amount is not UNSET:
            field_dict["employerVoluntaryCpfAmount"] = employer_voluntary_cpf_amount
        if employer_voluntary_medi_save_amount is not UNSET:
            field_dict["employerVoluntaryMediSaveAmount"] = employer_voluntary_medi_save_amount
        if sdl_contribution_amount is not UNSET:
            field_dict["sdlContributionAmount"] = sdl_contribution_amount
        if employer_pension_contribution is not UNSET:
            field_dict["employerPensionContribution"] = employer_pension_contribution
        if employee_pension_contribution is not UNSET:
            field_dict["employeePensionContribution"] = employee_pension_contribution
        if employee_national_insurance_contribution is not UNSET:
            field_dict["employeeNationalInsuranceContribution"] = employee_national_insurance_contribution
        if employer_national_insurance_contribution is not UNSET:
            field_dict["employerNationalInsuranceContribution"] = employer_national_insurance_contribution
        if employee_pensionable_earnings is not UNSET:
            field_dict["employeePensionableEarnings"] = employee_pensionable_earnings
        if employer_pensionable_earnings is not UNSET:
            field_dict["employerPensionableEarnings"] = employer_pensionable_earnings
        if termination_payment_ni_exempt is not UNSET:
            field_dict["terminationPaymentNIExempt"] = termination_payment_ni_exempt
        if termination_payment_employer_ni is not UNSET:
            field_dict["terminationPaymentEmployerNI"] = termination_payment_employer_ni
        if nic_class_1a is not UNSET:
            field_dict["nicClass1A"] = nic_class_1a
        if enrolled_in_pension_scheme is not UNSET:
            field_dict["enrolledInPensionScheme"] = enrolled_in_pension_scheme
        if deferral_date is not UNSET:
            field_dict["deferralDate"] = deferral_date
        if bik_taxable_amount is not UNSET:
            field_dict["bikTaxableAmount"] = bik_taxable_amount
        if bik_tax_exempt_amount is not UNSET:
            field_dict["bikTaxExemptAmount"] = bik_tax_exempt_amount
        if cp_38_amount is not UNSET:
            field_dict["cp38Amount"] = cp_38_amount
        if pcb_borne_by_employer_amount is not UNSET:
            field_dict["pcbBorneByEmployerAmount"] = pcb_borne_by_employer_amount
        if epf_employer_amount is not UNSET:
            field_dict["epfEmployerAmount"] = epf_employer_amount
        if epf_employee_amount is not UNSET:
            field_dict["epfEmployeeAmount"] = epf_employee_amount
        if eis_employer_amount is not UNSET:
            field_dict["eisEmployerAmount"] = eis_employer_amount
        if eis_employee_amount is not UNSET:
            field_dict["eisEmployeeAmount"] = eis_employee_amount
        if socso_employer_amount is not UNSET:
            field_dict["socsoEmployerAmount"] = socso_employer_amount
        if socso_employee_amount is not UNSET:
            field_dict["socsoEmployeeAmount"] = socso_employee_amount
        if hrdf_amount is not UNSET:
            field_dict["hrdfAmount"] = hrdf_amount

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        id = d.pop("id", UNSET)

        total_hours = d.pop("totalHours", UNSET)

        gross_earnings = d.pop("grossEarnings", UNSET)

        pre_tax_deductions = d.pop("preTaxDeductions", UNSET)

        taxable_earnings = d.pop("taxableEarnings", UNSET)

        post_tax_deductions = d.pop("postTaxDeductions", UNSET)

        net_earnings = d.pop("netEarnings", UNSET)

        total_employee_expenses = d.pop("totalEmployeeExpenses", UNSET)

        total_employer_liabilities = d.pop("totalEmployerLiabilities", UNSET)

        is_published = d.pop("isPublished", UNSET)

        pay_run_id = d.pop("payRunId", UNSET)

        notes = d.pop("notes", UNSET)

        notation = d.pop("notation", UNSET)

        payg_withheld = d.pop("paygWithheld", UNSET)

        sfss_withheld = d.pop("sfssWithheld", UNSET)

        help_withheld = d.pop("helpWithheld", UNSET)

        super_contribution = d.pop("superContribution", UNSET)

        employer_contribution = d.pop("employerContribution", UNSET)

        kiwi_saver_employee_contribution = d.pop("kiwiSaverEmployeeContribution", UNSET)

        kiwi_saver_employer_contribution = d.pop("kiwiSaverEmployerContribution", UNSET)

        esct_contribution = d.pop("esctContribution", UNSET)

        student_loan_amount = d.pop("studentLoanAmount", UNSET)

        post_grad_loan_amount = d.pop("postGradLoanAmount", UNSET)

        student_loan_additional_mandatory_amount = d.pop("studentLoanAdditionalMandatoryAmount", UNSET)

        student_loan_additional_voluntary_amount = d.pop("studentLoanAdditionalVoluntaryAmount", UNSET)

        acc_levy_amount = d.pop("accLevyAmount", UNSET)

        cpf_employer_contribution_amount = d.pop("cpfEmployerContributionAmount", UNSET)

        cpf_employee_contribution_amount = d.pop("cpfEmployeeContributionAmount", UNSET)

        employer_voluntary_cpf_amount = d.pop("employerVoluntaryCpfAmount", UNSET)

        employer_voluntary_medi_save_amount = d.pop("employerVoluntaryMediSaveAmount", UNSET)

        sdl_contribution_amount = d.pop("sdlContributionAmount", UNSET)

        employer_pension_contribution = d.pop("employerPensionContribution", UNSET)

        employee_pension_contribution = d.pop("employeePensionContribution", UNSET)

        employee_national_insurance_contribution = d.pop("employeeNationalInsuranceContribution", UNSET)

        employer_national_insurance_contribution = d.pop("employerNationalInsuranceContribution", UNSET)

        employee_pensionable_earnings = d.pop("employeePensionableEarnings", UNSET)

        employer_pensionable_earnings = d.pop("employerPensionableEarnings", UNSET)

        termination_payment_ni_exempt = d.pop("terminationPaymentNIExempt", UNSET)

        termination_payment_employer_ni = d.pop("terminationPaymentEmployerNI", UNSET)

        nic_class_1a = d.pop("nicClass1A", UNSET)

        enrolled_in_pension_scheme = d.pop("enrolledInPensionScheme", UNSET)

        _deferral_date = d.pop("deferralDate", UNSET)
        deferral_date: Union[Unset, datetime.datetime]
        if isinstance(_deferral_date, Unset):
            deferral_date = UNSET
        else:
            deferral_date = isoparse(_deferral_date)

        bik_taxable_amount = d.pop("bikTaxableAmount", UNSET)

        bik_tax_exempt_amount = d.pop("bikTaxExemptAmount", UNSET)

        cp_38_amount = d.pop("cp38Amount", UNSET)

        pcb_borne_by_employer_amount = d.pop("pcbBorneByEmployerAmount", UNSET)

        epf_employer_amount = d.pop("epfEmployerAmount", UNSET)

        epf_employee_amount = d.pop("epfEmployeeAmount", UNSET)

        eis_employer_amount = d.pop("eisEmployerAmount", UNSET)

        eis_employee_amount = d.pop("eisEmployeeAmount", UNSET)

        socso_employer_amount = d.pop("socsoEmployerAmount", UNSET)

        socso_employee_amount = d.pop("socsoEmployeeAmount", UNSET)

        hrdf_amount = d.pop("hrdfAmount", UNSET)

        pay_run_total_model = cls(
            id=id,
            total_hours=total_hours,
            gross_earnings=gross_earnings,
            pre_tax_deductions=pre_tax_deductions,
            taxable_earnings=taxable_earnings,
            post_tax_deductions=post_tax_deductions,
            net_earnings=net_earnings,
            total_employee_expenses=total_employee_expenses,
            total_employer_liabilities=total_employer_liabilities,
            is_published=is_published,
            pay_run_id=pay_run_id,
            notes=notes,
            notation=notation,
            payg_withheld=payg_withheld,
            sfss_withheld=sfss_withheld,
            help_withheld=help_withheld,
            super_contribution=super_contribution,
            employer_contribution=employer_contribution,
            kiwi_saver_employee_contribution=kiwi_saver_employee_contribution,
            kiwi_saver_employer_contribution=kiwi_saver_employer_contribution,
            esct_contribution=esct_contribution,
            student_loan_amount=student_loan_amount,
            post_grad_loan_amount=post_grad_loan_amount,
            student_loan_additional_mandatory_amount=student_loan_additional_mandatory_amount,
            student_loan_additional_voluntary_amount=student_loan_additional_voluntary_amount,
            acc_levy_amount=acc_levy_amount,
            cpf_employer_contribution_amount=cpf_employer_contribution_amount,
            cpf_employee_contribution_amount=cpf_employee_contribution_amount,
            employer_voluntary_cpf_amount=employer_voluntary_cpf_amount,
            employer_voluntary_medi_save_amount=employer_voluntary_medi_save_amount,
            sdl_contribution_amount=sdl_contribution_amount,
            employer_pension_contribution=employer_pension_contribution,
            employee_pension_contribution=employee_pension_contribution,
            employee_national_insurance_contribution=employee_national_insurance_contribution,
            employer_national_insurance_contribution=employer_national_insurance_contribution,
            employee_pensionable_earnings=employee_pensionable_earnings,
            employer_pensionable_earnings=employer_pensionable_earnings,
            termination_payment_ni_exempt=termination_payment_ni_exempt,
            termination_payment_employer_ni=termination_payment_employer_ni,
            nic_class_1a=nic_class_1a,
            enrolled_in_pension_scheme=enrolled_in_pension_scheme,
            deferral_date=deferral_date,
            bik_taxable_amount=bik_taxable_amount,
            bik_tax_exempt_amount=bik_tax_exempt_amount,
            cp_38_amount=cp_38_amount,
            pcb_borne_by_employer_amount=pcb_borne_by_employer_amount,
            epf_employer_amount=epf_employer_amount,
            epf_employee_amount=epf_employee_amount,
            eis_employer_amount=eis_employer_amount,
            eis_employee_amount=eis_employee_amount,
            socso_employer_amount=socso_employer_amount,
            socso_employee_amount=socso_employee_amount,
            hrdf_amount=hrdf_amount,
        )

        pay_run_total_model.additional_properties = d
        return pay_run_total_model

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
